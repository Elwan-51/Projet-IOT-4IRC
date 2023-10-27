from fastapi.security import OAuth2PasswordBearer
import json

with open('../config.json', 'r') as config_file:
    config = json.load(config_file)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
