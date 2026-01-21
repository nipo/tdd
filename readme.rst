=======================
 2D-Doc parser library
=======================

This is a `2D-Doc <2ddoc>`_ parser library. It is able to decode and
pretty-print a 2D-Doc as defined by French ANTS, and is also able to
verify signature.

Usage
=====

Dumper
------

There is a built-in dumper tool that can be called through command
line with:

.. code:: shell

  $ python3 -m tdd.dump tests/spec_samples/3.1.3/15.2.2/17.txt
  tests/spec_samples/3.1.3/15.2.2/17.txt:
  Version: 3
  Country: FR
  CA: FR00
  Cert: 0001
  Emit date: 2179-06-06
  Sign date: 2017-06-18
  Emitter doc type: Carte T3P
  User doc type: Justificatif d'activité
  Identifiants de données relatives aux véhicules
    Numéro de la carte: 12345678901
    Date d’expiration initiale: 2019-11-30
  Sign: a06b0fb1979c3a526d797a019c78f969a09d9973553d3e353d79a4a29041a4100792ccce10821f328046a36a024a2f47366c2df0cc627344d2070aa987c8e047
  Signature OK

API
---

A basic parsing sessions boils down to:

.. code:: python

  >>> from tdd.doc import TwoDDoc
  >>> c = TwoDDoc.from_code(open('tests/spec_samples/3.1.3/15.2.2/17.txt', 'r').read().strip())
  >>> c.header.doc_type().user_type
  "Justificatif d'activité"
  >>> c.header.doc_type().emitter_type
  'Carte T3P'
  >>> c.message.dataset
  [<tdd.message.FixedData object at 0x10ab320a0>, <tdd.message.FixedData object at 0x10ab32310>]
  >>> c.message.dataset[0].definition.name
  'Numéro de la carte'
  >>> c.message.dataset[0].value
  '12345678901'
  >>> from tdd.keychain import internal
  >>> chain = internal()
  >>> c.header.ca_id
  'FR00'
  >>> c.header.cert_id
  '0001'
  >>> c.signature_is_valid(chain)
  True

TODO
====

* Documentation

  * Full API documentation, better pydoc strings.

* Support for "binary" V4 messages

  * And support for V4 ancillary data

* Proper certificate chain handling

  * Full certificate chain verification

  * Verify revocation lists

  * Verify certificate validity time

License
=======

MIT.

.. _2ddoc: https://ants.gouv.fr/Les-solutions/2D-Doc
