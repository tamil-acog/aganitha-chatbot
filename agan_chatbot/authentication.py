import getpass
import os
import pickle
import base64

creds_file = 'creds.xyz'


def insert_user(username=None, password=None):
    """
    don't run this function directly, plese run authorise_user() which itself calls this function internally.
    :param username: organisation email
    :param password: password of your choice
    :return: None
    """
    if username is None:
        username = input("Enter Your organisation email : ")
    if password is None:
        password = getpass.getpass("Enter Your Password : ", stream=None)
    crds = {username: base64.b64encode(password.encode("utf-8"))}

    if creds_file in os.listdir():
        with open(creds_file, 'rb') as f:
            ext_crds = pickle.load(f)
            with open(creds_file, 'wb') as f:
                ext_crds.update(crds)
                pickle.dump(ext_crds, f)
                print(f'user {username} inserted')
    else:
        with open(creds_file, 'wb') as f:
            pickle.dump(crds, f)
        print('user inserted')


def update_password():
    """
    this function updates the user creds if needed
    :return:
    """
    with open(creds_file, 'rb') as f:
        ext_crds = pickle.load(f)

    username = input("Enter Your organisation email : ")
    password = getpass.getpass("Enter Your Password : ", stream=None)
    crds = {username: base64.b64encode(password.encode("utf-8"))}
    if username in ext_crds.keys():
        consent = input('user already exists, do you want to update creds with the current one ? yes or no.')
        if consent == 'yes':
            ext_crds.update(crds)
            print(f'user {username} creds updated')
        else:
            print('no changes made')


def authorise_user():
    """
    use this function to authorise the user and insert it if they dont exists
    make sure you are using your organisation emails as username.

    :return: None
    """
    ext_crds = None
    if creds_file in os.listdir():
        with open(creds_file, 'rb') as f:
            ext_crds = pickle.load(f)

    name = input("Enter Your organisation email : ")
    password = getpass.getpass("Enter Your Password : ")
    if ext_crds is None:
        print('user not registered, signing-up')
        insert_user(name, password)
    elif name not in ext_crds.keys():
        print('user not found, signing it up')
        insert_user(name, password)

    with open(creds_file, 'rb') as f:
        ext_crds = pickle.load(f)
    for i in ext_crds.keys():
        if name == i:
            while password != base64.b64decode(ext_crds.get(i)).decode("utf-8"):
                password = getpass.getpass("Enter Your Password Again : ")
            break
    print("Verified")
    return name


if __name__ == '__main__':
    authorise_user()
