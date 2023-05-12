import crypto from 'crypto'

export function randomString(size = 40) {  
  return crypto.randomBytes(size)
    .toString('hex')
    .slice(0, size)
}