# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Extractor for DataLad dataset metadata - ported from datalad-metalad"""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import os.path as op
import time

import datalad.support.network as dsn
from datalad_next.constraints import EnsureBool
from datalad_next.constraints.dataset import EnsureDataset


def get_dataset_metadata(ds, refcommit, status):
    meta = []
    # Get dataset commit info
    commitinfo = get_commit_info(ds, refcommit)
    # Get contributors from commits
    contributor_ids = []
    for contributor in commitinfo.pop("contributors", []):
        contributor_id = get_agent_id(*contributor[:2])
        meta.append(
            {
                "@id": contributor_id,
                # we cannot distinguish real people from machine-committers
                "@type": "agent",
                "name": contributor[0],
                "email": contributor[1],
            }
        )
        contributor_ids.append(contributor_id)
    # Set up dataset metadata dict
    dsmeta = {
        # the uniquest ID for this metadata record is the refcommit SHA
        "@id": refcommit,
        # the dataset UUID is the main identifier
        "identifier": ds.id,
        "@type": "Dataset",
    }
    dsmeta.update(commitinfo)
    # Add contributors
    if contributor_ids:
        c = [{"@id": i} for i in contributor_ids]
        dsmeta["hasContributor"] = c[0] if len(c) == 1 else c
    # Add subdatasets
    parts = []
    for subds in [s for s in status if s["type"] == "dataset"]:
        subdsinfo = {
            # reference by subdataset commit
            "@id": "datalad:{}".format(subds["gitshasum"]),
            "@type": "Dataset",
            "name": Path(subds["path"]).relative_to(ds.pathobj).as_posix(),
        }
        subdsid = ds.subdatasets(
            contains=subds["path"],
            return_type="item-or-list",
            result_renderer="disabled",
        ).get("gitmodule_datalad-id", None)
        if subdsid:
            subdsinfo["identifier"] = "datalad:{}".format(subdsid)
        parts.append(subdsinfo)
    if parts:
        dsmeta["hasPart"] = parts
    # Add distributions
    if ds.config.obtain(
        "datalad.metadata.datalad-core.report-remotes",
        True,
        valtype=EnsureBool(),
    ):
        remote_names = ds.repo.get_remotes()
        distributions = []
        known_uuids = {}
        # start with configured Git remotes
        for r in remote_names:
            info = {
                "name": r,
                # not very informative
                #'description': 'DataLad dataset sibling',
            }
            url = ds.config.get("remote.{}.url".format(r), None)
            # best effort to recode whatever is configured into a URL
            if url is not None:
                url = ri2url(dsn.RI(url))
            if url:
                info["url"] = url
            # do we have information on the annex ID?
            annex_uuid = ds.config.get("remote.{}.annex-uuid".format(r), None)
            if annex_uuid is not None:
                info["@id"] = "datalad:{}".format(annex_uuid)
                known_uuids[annex_uuid] = info
            if "url" in info or "@id" in info:
                # only record if we have any identifying information
                # otherwise it is pointless cruft
                distributions.append(info)
        # now look for annex info
        if hasattr(ds.repo, "repo_info"):
            info = ds.repo.repo_info(fast=True)
            for cat in (
                "trusted repositories",
                "semitrusted repositories",
                "untrusted repositories",
            ):
                for r in info[cat]:
                    if r["here"] or r["uuid"] in (
                        "00000000-0000-0000-0000-000000000001",
                        "00000000-0000-0000-0000-000000000002",
                    ):
                        # ignore local and universally available
                        # remotes
                        continue
                    # avoid duplicates, but record all sources, even
                    # if not URLs are around
                    if r["uuid"] not in known_uuids:
                        distributions.append({"@id": r["uuid"]})
        if distributions:
            dsmeta["distribution"] = sorted(
                distributions, key=lambda x: x.get("@id", x.get("url", None))
            )
        meta.append(dsmeta)
    return meta


def get_commit_info(ds, refcommit):
    """Get info about all commits, up to (and incl. the refcommit)"""
    # - get all the commit info with git log --pretty='%aN%x00%aI%x00%H'
    #  - use all first-level paths other than .datalad and .git for the query
    # - from this we can determine all modification timestamps, described refcommit
    # - do a subsequent git log query for the determined refcommit to determine
    #  a version by counting all commits since inception up to the refcommit
    #  - we cannot use the first query, because it will be constrained by the
    #    present paths that may not have existed previously at all

    # grab the history until the refcommit
    commits = [
        line.split("\0")
        for line in ds.repo.call_git_items_(
            # name, email, timestamp, shasum
            ["log", "--pretty=format:%aN%x00%aE%x00%aI%x00%H", refcommit]
        )
    ]
    # version, always anchored on the first commit (tags could move and
    # make the integer commit count ambiguous, and subtantially complicate
    # version comparisons
    version = "0-{}-g{}".format(
        len(commits),
        # abbreviated shasum (like git-describe)
        ds.repo.get_hexsha(commits[0][3], short=True),
    )
    meta = {
        "version": version,
    }
    if ds.config.obtain(
        "datalad.metadata.datalad-core.report-contributors",
        True,
        valtype=EnsureBool(),
    ):
        meta.update(contributors=sorted(set(tuple(c[:2]) for c in commits)))
    if ds.config.obtain(
        "datalad.metadata.datalad-core.report-modification-dates",
        True,
        valtype=EnsureBool(),
    ):
        meta.update(
            dateCreated=commits[-1][2],
            dateModified=commits[0][2],
        )
    return meta


def get_agent_id(name, email):
    """Return a suitable '@id' for committers/authors

    In most cases we will not have a URL for people/software agents.
    Let's create a string ID that is based on the combination of both
    name and email. Return an MD5 hash instead of a plain-text string
    to discourage direct interpretation by humans.
    """
    return hashlib.md5(
        "{}<{}>".format(name.replace(" ", "_"), email).encode("utf-8")
    ).hexdigest()


# TODO RF to be merged with datalad.support.network
def ri2url(ri):
    f = ri.fields
    if isinstance(ri, dsn.URL):
        return ri.as_str()
    elif isinstance(ri, dsn.SSHRI):
        # construct a URL that Git would understand
        return "ssh://{}{}{}{}{}{}".format(
            f["username"],
            "@" if f["username"] else "",
            f["hostname"],
            ":" if f["port"] else "",
            f["port"],
            f["path"]
            if op.isabs(f["path"])
            else "/{}".format(f["path"])
            if f["path"].startswith("~")
            else "/~/{}".format(f["path"]),
        )
    elif isinstance(ri, dsn.PathRI):
        # this has no chance of being resolved outside this machine
        # not work reporting
        return None


def get_dataset_url(graph):
    dataset = [x for x in graph if x["@type"] == "Dataset"]
    dataset = dataset[0]
    dist = dataset.get("distribution", [])
    return [d["url"] for d in dist if "url" in d]


def get_authors(graph):
    return [
        {"name": x["name"], "email": x["email"]}
        for x in graph
        if x["@type"] == "agent"
    ]


def get_subdatasets(graph):
    dataset = [x for x in graph if x["@type"] == "Dataset"]
    dataset = dataset[0]
    haspart = dataset.get("hasPart", [])
    subs = [
        {
            "dataset_id": h["identifier"].replace("datalad:", ""),
            "dataset_version": h["@id"].replace("datalad:", ""),
            "dataset_path": h["name"],
            "dirs_from_path": [],
        }
        for h in haspart
    ]
    return subs if len(subs) > 0 else None


def get_metadata_source(metadata_record):
    s = {
        "key_source_map": {},
        "sources": [
            {
                "source_name": metadata_record["extractor_name"],
                "source_version": metadata_record["extractor_version"],
                "source_parameter": metadata_record["extraction_parameter"],
                "source_time": metadata_record["extraction_time"],
                "agent_email": metadata_record["agent_email"],
                "agent_name": metadata_record["agent_name"],
            }
        ],
    }
    return s if len(s) > 0 else None


def translate(metadata_record, graph):
    translated_record = {
        "type": metadata_record["type"],
        "dataset_id": metadata_record["dataset_id"],
        "dataset_version": metadata_record["dataset_version"],
        "metadata_sources": get_metadata_source(metadata_record),
        "name": "",
        "url": get_dataset_url(graph),
        "authors": get_authors(graph),
        "subdatasets": get_subdatasets(graph),
    }
    return {k: v for k, v in translated_record.items() if v is not None}


# SCRIPT EXECUTION STARTS HERE

parser = ArgumentParser()
parser.add_argument(
    "dataset_path", type=Path, help="Path to the datalad dataset"
)
args = parser.parse_args()
source_dataset = EnsureDataset(
    installed=True, purpose="extract core metadata", require_id=True
)(args.dataset_path).ds
source_dataset_id = (source_dataset.id,)
source_dataset_version = source_dataset.repo.get_hexsha()
agent_name = source_dataset.config.get("user.name")
agent_email = source_dataset.config.get("user.email")
status = source_dataset.subdatasets(result_renderer="disabled")
metadata = get_dataset_metadata(source_dataset, source_dataset_version, status)
default_context = {
    # schema.org definitions by default
    "@vocab": "http://schema.org/",
    # DataLad ID prefix, pointing to our own resolver
    "datalad": "http://dx.datalad.org/",
}
# meta_out structures the metadata in exactly the same
# way as datalad meta-extract outputs it
meta_out = dict(
    dataset_id=source_dataset.id,
    dataset_version=source_dataset_version,
    extractor_name="catalog_core",
    extractor_version="1",
    extraction_parameter={},
    extraction_time=time.time(),
    agent_name=agent_name,
    agent_email=agent_email,
    extracted_metadata={
        "@context": default_context,
        "@graph": metadata,
    },
    type="dataset",
)
# translate() does more or less the same as
# datalad_catalog.translators.metalad_core_translator
meta_translated = translate(meta_out, metadata)
print(json.dumps(meta_translated))
