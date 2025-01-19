from __future__ import annotations

import sys 
import os
import time
import warnings

import cowsay
import dotenv
import requests
from google.oauth2.credentials import Credentials as OAuth2Credentials
from google.cloud.firestore import Client as FirestoreClient

# TODO: comment this next line and get rid of the deprecation warning instead of suppressing it 
warnings.simplefilter("ignore", UserWarning)

# get the firebase web api key 
dotenv_path = os.path.join(os.getcwd(), ".env")
assert dotenv.load_dotenv(dotenv_path) or (os.environ.get("FBASE_API_KEY") and os.environ.get("FBASE_PROJECT_ID")), "unable to read in firebase api key"

FBASE_API_KEY = os.environ["FBASE_API_KEY"]
FBASE_PROJECT_ID = os.environ["FBASE_PROJECT_ID"]

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

if sys.platform == "win32" or sys.platform == "darwin":

    # apparently this keyring lib supports both windows and mac 

    import keyring
    import keyring.errors
    
    # ensure correct backend is used
    if sys.platform == "win32":
        from keyring.backends.Windows import WinVaultKeyring as KeyringBackend
    else:
        from keyring.backends.macOS import Keyring as KeyringBackend
        
    if not isinstance(keyring.get_keyring(), KeyringBackend):
        keyring.set_keyring(KeyringBackend())
    
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
    #  no guarantee that keyring lib will have a backend to support it 
    #  so for now we do not support linux 
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
    
import firebase_admin
def is_subscription_active(
    access_tok: str, 
    refresh_tok: str, 
    user_id: str,
) -> bool:
    # make google oauth2 token
    creds = OAuth2Credentials(
        access_tok, 
        refresh_tok,
    )
    
    db = FirestoreClient(
        project=FBASE_PROJECT_ID,
        credentials=creds,
    )
    
    results = db.collection("customers", user_id, "subscriptions").where(
        "status", "==", "active" 
    ).stream()
    
    stat = False
    
    for doc in results:
        if doc.to_dict()["status"] == "active":
            # NOTE: in our implementation there 
            stat = True
    
    return stat
        

def get_cla_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--force-relogin",
        help="force relogin at the beginning of the application",
        action="store_true"
    )
    
    return parser


def main():
    # TODO: refactor the if statements
    cla_parser = get_cla_parser()
    
    args = cla_parser.parse_args()
    
    
    
    access_tok = get_acc_tok()  # either str or None
    refresh_tok = get_refresh_tok()  # either str or None
    
    if args.force_relogin:
        # force case 3
        access_tok = None
        refresh_tok = None
    
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
    
    print(f"hello, {user_data["email"]}, your userid is {user_data["localId"]}. Checking your subscription status....")
    
    
    sub_active = is_subscription_active(access_tok, refresh_tok, user_data["localId"])
    
    if sub_active:
        print("found an active subscription, accessig premium content...")
        print()
        cowsay.cow("mom deleted roblox uwu")
        print()
        
    else:
        print("active subscription not found, please go on your online profile and activate your premium account")

    time.sleep(2)

    logout_inp = input("would you like to log out? (y for yes) ")
    
    if logout_inp.lower().strip().startswith("y"):  # Y, y, yes, ye, YES, ...
        clear_tokens()
    
if __name__ == "__main__":
    main()