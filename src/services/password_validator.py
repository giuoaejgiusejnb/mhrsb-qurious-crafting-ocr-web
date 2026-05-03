from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool # パスワードがパスワードポリシーを満たすかどうか
    errors: list[str] # エラーメッセージのリスト
    
    # エラーメッセージを繋げて返す
    def join_errors(self, separator: str = "\n") -> str:
        return separator.join(self.errors)

class PasswordValidator:
    def __init__(
        self,
        min_length: int = 6, # パスワードの最小の長さ
        require_digit: bool = False, # パスワードに数字が必要か
        require_uppercase: bool = False # パスワードに英大文字が必要か
    ) -> None:
        self.min_length = min_length
        self.require_digit = require_digit
        self.require_uppercase = require_uppercase

    def check(self, password: str) -> ValidationResult:
        errors: list[str] = []

        if len(password) < self.min_length:
            errors.append(f"パスワードは{self.min_length}文字以上必要です")
        
        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("パスワードには数字を1つ以上含めてください")
            
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("パスワードには英大文字を1つ以上含めてください")

        return  ValidationResult(is_valid=(len(errors) == 0), errors=errors)