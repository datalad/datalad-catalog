# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Extractor for DataLad dataset runrecord metadata - ported from datalad-metalad"""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import os
import time

from datalad_catalog.schema_utils import (
    get_metadata_item,
)
from datalad.support.json_py import (
    loads as jsonloads,
    load as jsonload,
)
from datalad_next.constraints.dataset import EnsureDataset


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


def get_file_id(rec):
    """Returns a suitable '@id' of a file metadata from a status result

    Prefer a present annex key, but fall back on the Git shasum that is
    always around. Identify the GITSHA as such, and in a similar manner
    to git-annex's style.

    Any ID string is prefixed with 'datalad:' to identify it as a
    DataLad-recognized ID. This prefix is defined in the main JSON-LD
    context definition.
    """
    from datalad.support.digests import Digester

    id_ = (
        rec["key"]
        if "key" in rec
        else "SHA1-s{}--{}".format(
            rec["bytesize"]
            if "bytesize" in rec
            else 0
            if rec["type"] == "symlink"
            else os.stat(rec["path"]).st_size,
            rec["gitshasum"]
            if "gitshasum" in rec
            else Digester(digests=["sha1"])(rec["path"])["sha1"],
        )
    )
    return "datalad:{}".format(id_)


def translate(metadata_record):
    meta_item = get_metadata_item(
        item_type=metadata_record["type"],
        dataset_id=metadata_record["dataset_id"],
        dataset_version=metadata_record["dataset_version"],
        source_name=metadata_record["extractor_name"],
        source_version=metadata_record["extractor_version"],
    )
    meta_item["provenance"] = translate_provenance(metadata_record)
    return {k: v for k, v in meta_item.items() if v is not None}


def translate_provenance(metadata_record):
    """"""
    current_dsid = metadata_record["dataset_id"]
    graph = metadata_record["extracted_metadata"]["@graph"]
    # list to store output
    provenance = []
    # Get all agents
    agents = [
        (
            a["@id"],
            {
                "name": a["name"],
                "email": a["email"],
            },
        )
        for a in graph
        if a.get("@type") == "agent"
    ]
    agents = dict(agents)
    # Find all activities, i.e. run records
    runrecords = [r for r in graph if r.get("@type") == "activity"]
    for r in runrecords:
        rdict = {
            "type": "run_record",
            "dataset_version": r.get("@id"),
            "previous_version": r.get("previous_gitsha"),
            "datetime": r.get("atTime"),
            "description": r.get("rdfs:comment"),
            "chain": r.get("run_record", {}).get("chain"),
            "cmd": r.get("run_record", {}).get("cmd"),
            "exit": r.get("run_record", {}).get("exit"),
            "extra_inputs": r.get("run_record", {}).get("extra_inputs"),
            "inputs": r.get("run_record", {}).get("inputs"),
            "outputs": r.get("run_record", {}).get("outputs"),
            "pwd": r.get("run_record", {}).get("pwd"),
            "author": agents.get(
                r.get("prov:wasAssociatedWith").get("@id"),
                {"name": "", "email": ""},
            ),
        }
        provenance.append(rdict)
    return provenance


def get_runprov_metadata(dataset, refcommit, process_type, status):
    ds = dataset

    # lookup dict to find an activity that generated a file at a particular
    # path
    path_db = {}
    # all discovered activities indexed by their commit sha
    activities = {}

    for rec in yield_run_records(ds):
        # run records are coming in latest first
        for d in rec.pop("diff", []):
            if d["path"] in path_db:
                # records are latest first, if we have an entry, we already
                # know about the latest change
                continue
            if d["mode"] == "000000":
                # this file was deleted, hence it cannot possibly be part
                # of the to-be-described set of files
                continue
            # record which activity generated this file
            path_db[d["path"]] = dict(
                activity=rec["gitshasum"],
                # we need to capture the gitshasum of the file as generated
                # by the activity to be able to discover later modification
                # between this state and the to-be-described state
                gitshasum=d["gitshasum"],
            )
        activities[rec["gitshasum"]] = rec

    yielded_files = False
    if process_type and process_type == "all":
        for rec in status:
            # see if we have any knowledge about this entry
            # from any of the activity change logs
            dbrec = path_db.get(
                Path(rec["path"]).relative_to(ds.pathobj).as_posix(), {}
            )
            if dbrec.get("gitshasum", None) == rec.get("gitshasum", ""):
                # the file at this path was generated by a recorded
                # activity
                yield dict(
                    rec,
                    metadata={
                        "@id": get_file_id(rec),
                        "@type": "entity",
                        "prov:wasGeneratedBy": {
                            "@id": dbrec["activity"],
                        },
                    },
                    type=rec["type"],
                    status="ok",
                )
                yielded_files = True
            else:
                # we don't know an activity that made this file, but we
                # could still report who has last modified it
                # no we should not, this is the RUN provenance extractor
                # this stuff can be done by the core extractor
                pass
    agents = {}
    graph = []
    for actsha in sorted(activities):
        rec = activities[actsha]
        agent_id = get_agent_id(rec["author_name"], rec["author_email"])
        # do not report docs on agents immediately, but collect them
        # and give unique list at the end
        agents[agent_id] = dict(
            name=rec["author_name"], email=rec["author_email"]
        )
        previous_gitsha = dataset.repo.call_git(
            ["log", "--pretty=%P", "-n", "1", actsha]
        )
        graph.append(
            {
                "@id": actsha,
                "@type": "activity",
                "atTime": rec["commit_date"],
                "prov:wasAssociatedWith": {
                    "@id": agent_id,
                },
                # TODO extend message with formatted run record
                # targeted for human consumption (but consider
                # possible leakage of information from sidecar
                # runrecords)
                "rdfs:comment": rec["message"],
                "run_record": rec["run_record"],
                "previous_gitsha": previous_gitsha.rstrip(),
            }
        )
    # and now documents on the committers
    # this is likely a duplicate of a report to be expected by
    # the datalad_core extractor, but over there it is configurable
    # and we want self-contained reports per extractor
    # the redundancy will be eaten by XZ compression
    for agent in sorted(agents):
        rec = agents[agent]
        graph.append(
            {
                "@id": agent,
                "@type": "agent",
                "name": rec["name"],
                "email": rec["email"],
            }
        )

    yield dict(
        metadata={
            "@context": "http://openprovenance.org/prov.jsonld",
            "@graph": graph,
        },
        type="dataset",
        status="ok",
    )


def yield_run_records(ds):
    def _split_record_message(lines):
        msg = []
        run = []
        inrec = False
        for line in lines:
            if line == "=== Do not change lines below ===":
                inrec = True
            elif line == "^^^ Do not change lines above ^^^":
                inrec = False
            elif inrec:
                run.append(line)
            else:
                msg.append(line)
        return "\n".join(msg).strip(), "".join(run)

    def _finalize_record(r):
        msg, rec = _split_record_message(r.pop("body", []))
        r["message"] = msg
        # TODO this can also just be a runrecord ID in which case we need
        # to load the file and report its content
        rec = jsonloads(rec)
        if not isinstance(rec, dict):
            # this is a runinfo file name
            rec = jsonload(
                str(ds.pathobj / ".datalad" / "runinfo" / rec),
                # TODO this should not be necessary, instead jsonload()
                # should be left on auto, and `run` should save compressed
                # files with an appropriate extension
                compressed=True,
            )
        r["run_record"] = rec
        return r

    record = None
    indiff = False
    for line in ds.repo.call_git_items_(
        [
            "log",
            "-F",
            "--grep",
            "=== Do not change lines below ===",
            "--pretty=tformat:%x00%x00record%x00%n%H%x00%aN%x00%aE%x00%aI%n%B%x00%x00diff%x00",
            "--raw",
            "--no-abbrev",
        ]
    ):
        if line == "\0\0record\0":
            indiff = False
            # fresh record
            if record:
                yield _finalize_record(record)
            record = None
        elif record is None:
            record = dict(
                zip(
                    ("gitshasum", "author_name", "author_email", "commit_date"),
                    line.split("\0"),
                )
            )
            record["body"] = []
            record["diff"] = []
        elif line == "\0\0diff\0":
            indiff = True
        elif indiff:
            if not line.startswith(":"):
                continue
            diff = line[1:].split(" ")[:4]
            diff.append(line[line.index("\t") + 1 :])
            record["diff"].append(
                dict(
                    zip(
                        (
                            "prev_mode",
                            "mode",
                            "prev_gitshasum",
                            "gitshasum",
                            "path",
                        ),
                        diff,
                    )
                )
            )
        else:
            record["body"].append(line)
    if record:
        yield _finalize_record(record)


# TODO report runrecord directory as content-needed, if configuration wants this
# information to be reported. However, such files might be used to prevent leakage
# of sensitive information....


def get_catalog_metadata(source_dataset, process_type):
    """"""
    source_dataset_version = source_dataset.repo.get_hexsha()
    status = source_dataset.status(annex=True, result_renderer="disabled")
    agent_name = source_dataset.config.get("user.name")
    agent_email = source_dataset.config.get("user.email")

    metagraph = []

    for m in get_runprov_metadata(
        source_dataset, source_dataset_version, process_type, status
    ):
        metagraph = metagraph + m["metadata"]["@graph"]

    default_context = {
        # schema.org definitions by default
        "@vocab": "http://schema.org/",
        # DataLad ID prefix, pointing to our own resolver
        "datalad": "http://dx.datalad.org/",
        "prov": "http://openprovenance.org/prov.jsonld",
    }
    # meta_out structures the metadata in exactly the same
    # way as datalad meta-extract outputs it
    meta_out = dict(
        dataset_id=source_dataset.id,
        dataset_version=source_dataset_version,
        extractor_name="catalog_runprov",
        extractor_version="1",
        extraction_parameter={},
        extraction_time=time.time(),
        agent_name=agent_name,
        agent_email=agent_email,
        extracted_metadata={
            "@context": default_context,
            "@graph": metagraph,
        },
        type="dataset",
    )
    return translate(meta_out)


# SCRIPT EXECUTION STARTS HERE

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "dataset_path", type=Path, help="Path to the datalad dataset"
    )
    parser.add_argument(
        "--process_type",
        type=str,
        default="dataset",
        help="Only 'dataset' is supported at the moment",
    )
    args = parser.parse_args()
    source_dataset = EnsureDataset(
        installed=True, purpose="extract runrecord metadata", require_id=True
    )(args.dataset_path).ds
    process_type = args.process_type

    if process_type != "dataset":
        raise ValueError(
            "'process_type' argument can only have the value 'dataset'"
        )

    metadata = get_catalog_metadata(source_dataset, process_type)
    print(json.dumps(metadata))
