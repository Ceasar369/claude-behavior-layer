# The Vendor Glossary

Up: [[the-stack-MOC|The Stack]]

Nine words for everything between our code and an outside company, and where each sits.

## vendor

An outside company: a mail sender, a bank, a storage provider. A real
company, with a real agreement.

Or a program we run on our own server, with no agreement.

## vendor capability

The job we take from a company. Never the company itself.

Sending an email is one, called `mail`.

## vendor shape

The capability written down. What any answer must satisfy.

The mail shape holds one thing: send. It takes what its layer's email
carries: an address, a subject, a body, and any sender, reply address or
attachment.

It names no company, unless the person picks one. A new sender leaves it unchanged.

## vendor adapter

One company made to fit one shape.

The adapter for a mail company answers the mail shape by calling that company.

It is the only backend file holding that company's address and key. A
frontend loading a company's own script names that script's address.

Two senders are two adapters.

## vendor translator

One company's answers turned into what the shape returns.

The adapter calls the company. Its translator reads what came back.

## fake

A company's stand-in, for tests only. A test sets it in the company's place.

## vendor stub

An adapter with no company behind it.

It answers the shape, and no email leaves the machine.

It prints the message to the terminal instead.

It exists so a laptop runs before a company says yes.

## vendor choice

The one file selecting which adapter answers.

It refuses a stub in live mode, and an unknown name, at boot.

One per layer. It names every company that layer reaches.

## vendor name

The string the choice reads. It lives in the environment.

`MAIL_VENDOR=stub` on a laptop. The company's own name in production.

A different company is one line, and no code.

A capability may offer `none`: no company. The layer still boots, and that capability stays off.

## Where the nine sit

### One folder beside the backend

```
code/<layer>/
  backend/
  vendors/
    vendor-choice.ts
    vendor-capabilities/
      <capability>/
        vendor-shape.ts
        vendor-adapter-<company>.ts
        vendor-translator-<company>.ts
        vendor-stub.ts
        fake-<name>.ts
```

Every segment names its term. A full path explains itself.

### The folder reads alone

`vendors/` never imports from `backend/`.

The backend imports the choice.

### Every capability folder is closed

A second capability is a second folder under `vendor-capabilities/`.

A second company is a second adapter, beside the first.

Nothing crosses between two capability folders.

### Two layers may reach one company

Each holds its own adapter, and its own copy of the shape.

Two layers' vendor folders share no file.
