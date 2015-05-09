#! /bin/bash

psql -U postgres -d postgres -f dbUser.sql
psql -U postgres -d postgres -c "DROP DATABASE intellinews;"
psql -U postgres -d postgres -c "CREATE DATABASE intellinews WITH owner=foo ENCODING='utf-8';"

psql -U foo -d intellinews -f schema.sql
