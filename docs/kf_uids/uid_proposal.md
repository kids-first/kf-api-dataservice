# Proposal

Based on [uid_considerations.md](uid_considerations.md) and [uid_migration.md](uid_migration.md)

## 64 bit keys

### Nodeless (much better than what we have now)

* 31 bit seconds since custom epoch (now until 68 years from now)
* 33 bit randomized counter (8.5 billion keys for every second)
* Cross fingers

(Increasing to more bits would make it more better but also more bigger.)

### Nodefull

* 31 bit seconds since custom epoch (now until 68 years from now)
* 10 bit dataservice instance ID (1024 server instances)
  * Requires a dedicated ID assignment service (When an autoscale dataservice task spins up, the first thing it does is request a Node ID from a single task node assignment service. The assignment service just increments after each request up to 1024 and then resets.)
* 23 bit randomized counter (8 million keys in every second)

## Encoding

Studies need to keep old key format for compatibility with Amazon S3 bucket name restrictions, but we can improve the encoding for everything else.

Either base57 or better-than-crockford-base32 (see [uid_considerations.md # Modifying Crockford's Base32 symbol set](uid_considerations.md))

| Bits | Base32 Digits | Base57 Digits |
|-|-|-|
|64|13|11|

## Migration Plan

See [uid_migration.md](uid_migration.md)

## What about clients generating their own UIDs completely offline?

There's no value in being _always_ _completely_ offline. The dataservice can have a keyservice endpoint that hands out batches of up to, for instance, 1 million keys at a time to anyone who requests them. If the client then wants to use those as a key pool, that's fine.
