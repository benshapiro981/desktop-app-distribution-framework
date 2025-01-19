from __future__ import annotations

import sys 
import os
import time

import dotenv
import requests

# get the firebase web api key 
dotenv_path = os.path.join(os.getcwd(), ".env")
assert dotenv.load_dotenv(dotenv_path) or os.environ.get("FBASE_API_KEY"), "unable to read in firebase api key"

FBASE_API_KEY = os.environ["FBASE_API_KEY"]

def get_user_data(access_tok: str) -> dict | None:
    resp = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:lookup",
        params={"key": FBASE_API_KEY},
        data={
            "idToken": access_tok,
        }
    )
    
    if resp.status_code != 200:
        # either user not found or invalid token 
        return
    else:
        return resp.json()["users"][0]


def refresh_tokens(refresh_tok: str) -> tuple[None, None] | tuple[str, str]:
    print("attempting refresh...")
    resp = requests.post(
        "https://securetoken.googleapis.com/v1/token",
        params={"key": FBASE_API_KEY},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_tok,
        }
    )
    
    if resp.status_code != 200:
        # unable to refresh token for some reason 
        return None, None
    else:
        resp_decoded = resp.json()
        return str(resp_decoded["id_token"]), str(resp_decoded["refresh_token"])
    
def sign_in(email: str, pwd: str) -> tuple[str, str] | tuple[None, None]:
    resp = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
        params={"key": FBASE_API_KEY},
        data={
            "email": email,
            "password": pwd, 
            "returnSecureToken": True,
        }
    )
    
    if resp.status_code != 200:
        return None, None
    else:
        resp_decoded = resp.json()
        return str(resp_decoded["idToken"]), str(resp_decoded["refreshToken"])

if sys.platform == "win32":
    # for windows
    # TODO: implement the following functions
    #  note that they have uniform interface with mac os 
    
    # https://stackoverflow.com/questions/56068787/where-to-store-a-jwt-token-locally-on-computer
    
    def get_acc_tok() -> str | None:
        ...
        
    def get_refresh_tok() -> str | None:
        ...
    
    def set_acc_tok(tok: str) -> None:
        ...
        
    def set_refresh_tok(tok: str) -> None:
        ...
        
    def clear_acc_tok() -> None:
        ...
        
    def clear_refresh_tok() -> None:
        ...
    raise NotImplementedError

elif sys.platform == "darwin":
    # for mac os 
    import keyring
    import keyring.errors
    
    _service_name = "basic_app"
    _acc_tok_name = "acctok"
    _refresh_tok_name = "refreshtok"
    
    def get_acc_tok() -> str | None:
        return keyring.get_password(_service_name, _acc_tok_name)
        
    def get_refresh_tok() -> str | None:
        return keyring.get_password(_service_name, _refresh_tok_name)
    
    def set_acc_tok(tok: str) -> None:
        keyring.set_password(_service_name, _acc_tok_name, tok)
        
    def set_refresh_tok(tok: str) -> None:
        keyring.set_password(_service_name, _refresh_tok_name, tok)
        
    def clear_acc_tok() -> None:
        try:
            keyring.delete_password(_service_name, _acc_tok_name)
        except keyring.errors.PasswordDeleteError as e:
            # suppress exception if already deleted for idempotency
            if "item not found" not in str(e).lower():
                raise
            
    def clear_refresh_tok() -> None:
        try:
            keyring.delete_password(_service_name, _refresh_tok_name)
        except keyring.errors.PasswordDeleteError as e:
            # suppress exception if it is already deleted for idempotency 
            if "item not found" not in str(e).lower():
                raise

else:
    # for linux and other platformss
    #  problem with linux is that there is no good solution to securely store the tokens
    raise NotImplementedError

def clear_tokens() -> None:
    clear_acc_tok()
    clear_refresh_tok()

def login_loop() -> tuple[str, str]:
    try:
        while True:
            email = input("please enter email (or control-c to exit): ")
            pwd = input("please enter password (or control-c to exit): ")
            
            access_tok, refresh_tok = sign_in(email, pwd)
            
            if access_tok and refresh_tok and isinstance(access_tok, str) and isinstance(refresh_tok, str):
                return access_tok, refresh_tok
            
            print("invalid credentials supplied, please try again")
    except KeyboardInterrupt:  # don't want to print the exception stack 
        raise SystemExit(0)
        

def main():
    # TODO: refactor the if statements
    
    access_tok = get_acc_tok()  # either str or None
    refresh_tok = get_refresh_tok()  # either str or None
    
    user_data: dict | None = None
    if access_tok:
        # case 1: acc tok exists, so we check that it is valid
        user_data = get_user_data(access_tok)
        
        if user_data is None:
            clear_tokens()
            
            if refresh_tok:
                # in this case we attempt to refresh
                access_tok, refresh_tok = refresh_tokens(refresh_tok)
                
                if access_tok is None and refresh_tok is None:
                    # in this case we initiate login loop
                    
                    access_tok, refresh_tok = login_loop()
            
            else:
                # in this case we initiate login loop
                access_tok, refresh_tok = login_loop()
            
        
    elif refresh_tok: 
        # case 2: refresh tok exists, so we attempt to refresh
        clear_tokens()
        access_tok, refresh_tok = refresh_tokens(refresh_tok)
        
        if access_tok is None and refresh_tok is None:
            access_tok, refresh_tok = login_loop()
        
    else:
        # case 3: neither exists due to either first time login or user logged out previous session, so login
        clear_tokens()
        access_tok, refresh_tok = login_loop()
        
    assert access_tok and isinstance(access_tok, str)
    assert refresh_tok and isinstance(refresh_tok, str)
        
    set_acc_tok(access_tok)
    set_refresh_tok(refresh_tok)
        
    if user_data is None:
        user_data = get_user_data(access_tok)
        
    assert user_data and isinstance(user_data, dict)
    
    print(f"hello, {user_data["email"]}, your userid is {user_data["localId"]}. starting a long running task now....")
    time.sleep(10)
    print("task completed!")
    
    logout_inp = input("would you like to log out? (y for yes) ")
    
    if logout_inp.lower().strip().startswith("y"):  # Y, y, yes, ye, YES, ...
        clear_tokens()
    
if __name__ == "__main__":
    main()