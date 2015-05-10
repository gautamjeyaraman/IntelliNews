_CREATE_DOC = "INSERT INTO Document(title, uploaded_on, img_url, type) VALUES (%s, %s, %s, %s);"

_GET_ID_FROM_TITLE = 'SELECT id FROM Document WHERE title = %s;'
