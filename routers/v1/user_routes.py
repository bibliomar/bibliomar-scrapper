from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from services.user_functions import create_user, login_user, recover_user, change_password
from services.security.hashing_functions import jwt_validate, jwt_encode
from keys import email_url, email_pass, site_url
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.schemas import EmailStr

router = APIRouter(
    prefix="/v1"
)

email_str = EmailStr(email_url)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/login")

conf = ConnectionConfig(
    MAIL_USERNAME=email_url,
    MAIL_PASSWORD=email_pass,
    MAIL_FROM=email_str,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Biblioterra",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


# We use OAuth2 Password flow for better integration with the OpenAPI Schema

@router.get("/user/validate", tags=["user"])
async def user_validate(token: str = Depends(oauth2_scheme)):
    """
    Renews a token.
    """
    new_user_token = jwt_validate(token, 3)
    return {"access_token": new_user_token, "token_type": "bearer"}


@router.post("/user/signup", tags=["user"])
async def user_signup(form_data: OAuth2PasswordRequestForm = Depends(), email: str = Form(...)):
    """
    **WARNING:** <br>
    PLEASE make sure to not use passwords used elsewhere here. <br>
    Biblioterra is not proprietary software and the security services used are not hidden. <br>
    All passwords are hashed with
    [pbkdf2 - sha256](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.pbkdf2_digest.html#passlib.hash.pbkdf2_sha256) <br>
    """
    user_token = await create_user(form_data, email)
    return {"access_token": user_token, "token_type": "bearer"}


@router.post("/user/login", tags=["user"])
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Use this endpoint to authenticate users. <br>
    After authenticating, use the /library routes to populate the user's library. <br>
    Only username and password are needed.
    """
    user_token = await login_user(form_data)
    return {"access_token": user_token, "token_type": "bearer"}


@router.post("/user/recover", tags=["user"])
async def user_recover(email=Form(...)):
    user = await recover_user(email)
    username = user["username"]

    recover_token = jwt_encode(user["username"], 3)
    html = f"<h2>Recuperação de senha - Bibliomar</h2><br>" \
           f"Alguem (provavelmente você) solicitou uma troca de senha para a conta no Bibliomar.<br>" \
           f"Seu nome de usuario é: {username}" \
           f"Para trocar sua senha, basta acessar o link a seguir:<br><br>" \
           f"{site_url}/user/recover?token={recover_token} <br><br>" \
           f"Esse link é válido por 72 horas.<br>" \
           f"Caso não tenha sido você que solicitou essa troca, basta ignorar esse email. <br><br>" \
           f"<strong>Não compartilhe esse link com ninguém, ele garante acesso a sua conta e seus dados</strong>."

    message = MessageSchema(subject="Recuperação de senha - Bibliomar", recipients=[user["email"]], html=html)
    fm = FastMail(conf)
    await fm.send_message(message)

    return 200


@router.post("/user/change", tags=["user"])
async def user_change(token=Depends(oauth2_scheme), new_pass: str | None = Form(None),
                      new_email: str | None = Form(None)):
    await change_password(token, new_pass, new_email)
    return 200
