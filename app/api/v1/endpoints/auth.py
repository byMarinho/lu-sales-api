import logging
import sentry_sdk
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, verify_password
from app.repositories.user import create_user, get_user_by_email
from app.schemas.token import Token, LoginRequest
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer()

@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {
            "description": "Login bem-sucedido",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            },
        },
        401: {"description": "Credenciais incorretas"},
    },
)
def login(
    login_in: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Realiza login de usuário via e-mail e senha.

    - Retorna um token JWT válido para autenticação nos demais endpoints.
    - Retorna erro 401 caso o e-mail ou senha estejam incorretos.

    **Casos de uso:**
    - Login de administradores, vendedores ou usuários do sistema.
    - Obtenção de token para autenticação de rotas protegidas.
    """
    logger = logging.getLogger(__name__)
    try:
        user = get_user_by_email(db, email=login_in.email)

        if not user or not verify_password(login_in.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro inesperado no login: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")

@router.post(
    "/register",
    response_model=Token,
    responses={
        200: {
            "description": "Registro bem-sucedido",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            },
        },
        400: {"description": "Email já registrado"},
    },
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Realiza o cadastro de um novo usuário.

    - O e-mail deve ser único.
    - Retorna um token JWT válido para autenticação imediata após o cadastro.
    - Retorna erro 400 caso o e-mail já esteja cadastrado.

    **Casos de uso:**
    - Cadastro de administradores, vendedores ou usuários do sistema.
    - Permite login imediato após o registro.
    """
    logger = logging.getLogger(__name__)
    try:
        user = get_user_by_email(db, email=user_in.email)

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = create_user(db, user_in=user_in)
        access_token = create_access_token(data={"sub": str(user.id)})

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro inesperado no registro: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")

@router.post(
    "/refresh-token",
    response_model=Token,
    responses={
        200: {
            "description": "Token JWT renovado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            },
        },
        401: {"description": "Token inválido ou expirado"},
    },
)
def refresh_token(
    credentials=Security(HTTPBearer()),
    db: Session = Depends(get_db),
):
    """
    Gera um novo token JWT a partir de um token válido ainda não expirado.

    - O token antigo deve ser enviado no header Authorization: Bearer <token>.
    - Retorna erro 401 caso o token seja inválido ou expirado.
    - O novo token terá o tempo de expiração padrão do sistema.

    **Casos de uso:**
    - Renovação de sessão sem necessidade de login novamente.
    - Manutenção de usuários autenticados em aplicações web/mobile.
    """
    from jose import JWTError, jwt
    from app.core.config import settings
    from app.models.user import User

    logger = logging.getLogger(__name__)
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        logger.error("Erro inesperado na renovação de token: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
