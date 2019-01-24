# Proposal

Based on [uid_considerations.md](uid_considerations.md) and [uid_migration.md](uid_migration.md)

## 64+ bit nodeless keys

* 32 bit time in half-seconds since custom epoch (now until 68 years from now)
* 32+ bit randomized counter (4.3 billion+ keys for every half-second)
* Cross fingers gently

(Increasing to more bits would make it more better but also more bigger.)

(Switching to nodeful would make it more better but also more fragile.)

## Bit layout

The counter bits will be reversed (to put rapid changes at the left for easier left-to-right reading) and then the counter and timer bits will be interleaved (to distribute randomization across the whole key). The key, therefore, will begin with the lowest order bit from the counter and end with the lowest order bit from the timer.

e.g., for 5 bit timer `t`, 5 bit counter `c`:

|`t1`|`t2`|`t3`|`t4`|`t5`|`c1`|`c2`|`c3`|`c4`|`c5`|
|-|-|-|-|-|-|-|-|-|-|
| | | | |↓| | | | |
|`c5`|`t1`|`c4`|`t2`|`c3`|`t3`|`c2`|`t4`|`c1`|`t5`|

### Example keys ( see `uidtest.py`)

#### Example keys generated in the same half-second

(not ***very*** different, but at least different on the left):

```text
* 2YT6EP6V5RGV6
* AYT6EP6V5RGV6
* 8BT6EP6V5RGV6
* 0VT6EP6V5RGV6
* 0FT6EP6V5RGV6
* 8ZT6EP6V5RGV6
* AAGPEP6V5RGV6
* 2EGPEP6V5RGV6
* 2BGPEP6V5RGV6
* AFGPEP6V5RGV6
```

#### Example keys generated in different half-seconds

```text
* 0ATKEP4FDSGBD
* 8FGK674ADRJER
* 2ZTP674AD8RZV
* 0YT34PETF8RTP
* AEJJCPEZDXJZZ
* 2FGPE6EBFRKN8
* AFR34P6A5XSG1
* 2YR64K6BDWS4E
* 2FJ3E2CVDWSG5
* AFR7CKCE7CHMR
```

## Encoding

We will keep Crockford's base32 for simplicity.

## Migration Plan

See [uid_migration.md](uid_migration.md)
