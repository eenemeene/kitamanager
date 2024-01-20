Development
-----------

Die Entwicklung von `kitamanager` erfolgt auf `github <https://github.com/eenemeene/kitamanager>`_ .
Fragen und Fehlerberichte (bugs) bitte unter https://github.com/eenemeene/kitamanager/issues eintragen.

Tests ausführen
~~~~~~~~~~~~~~~

Test können mittels `tox` ausgeführt werden:

.. code-block:: shell

   tox

Entwicklungsumgebung aufsetzen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`kitamanager` benötigt Postgresql als Datenbank.
Einen Postgresql Datenbankserver kann mit einem Container
bereitgestellt werden:

.. code-block:: shell

   docker run --name kitamanager-postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=kitamanager -d postgres:16

Nun die entsprechenden Umgebungsvariablen setzen:

.. code-block:: shell

   source kitamanager-env-dev-postgres

Nun in einem virtualenv (hier im `py3` virtualenv von tox)
die entsprechenden Befehle zur Datenbankmigration usw:

.. code-block:: shell

   source .tox/py3/bin/activate
   ./manage.py migrate
   DJANGO_SUPERUSER_PASSWORD=admin ./manage.py createsuperuser --username admin --noinput --email admin@example.com
   ./manage.py childpayment_import berlin child-payment-berlin.yaml
   ./manage.py runserver

Jetzt sollte unter http://127.0.0.1:8000/ die Applikation laufen und ein login
mit Benutzername `admin` und Passwort `admin` funktionieren.


OCI Container bauen
~~~~~~~~~~~~~~~~~~~

Damit die Version korrekt gesetzt wird, muss der container mit folgendem Kommando gebaut werden:

.. code-block:: shell

   docker build --build-arg VERSION=$(cd django-kitamanager && python3 -m setuptools_scm) .
