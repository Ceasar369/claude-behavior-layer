# The Person Door

Up: [[the-stack-MOC|The Stack]]

How a person logs into one of our surfaces, everywhere.

## One person door per surface

Each surface holds one.

Every person door opens with a cookie.

## A login session is a row

The cookie carries the row's id, and nothing else.

Each door names its own cookie.

Deleting the row ends the login, everywhere.

A login keeps a person's sessions on other devices, on every door.

A password reset ends every session of that person.

A new password ends that person's other sessions.

A login session expires once unused too long.

Each use moves the cookie's end on with the row's.

Logging out leaves no page behind: Back, and every open tab, show the login.

A login session is never a Claude session, and never a port band.

## Every door logs in, logs out, and says who is in

A door with a team adds an invited teammate's first login.

## A wrong password answers like an unknown email

Same code. Same time.

The password check runs either way.

Once a person's row is deleted, their email answers a login as an unknown one does.

## The password check lives in one file

No dependency enters.

A provider can replace that file alone. The login session stays ours.

## One origin per surface

A frontend and its backend share one origin.

Never `SameSite=None`. Never a cookie across origins.

## Seeded people

One shared password, from the environment. Never in code.

A frontend reads it from its own environment. A built bundle never holds it.
