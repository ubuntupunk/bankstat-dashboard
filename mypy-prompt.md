You are tasked to add, improve or correct mypy typing for the my_project/my_app folder including the test files. You are NOT to add any typing to anything outside this folder. However, you might need to see other apps or folders if there's a reference to them in order to add the correct typing. Specifically, you should look at the my_project/sample_app folder for examples of how typing is applied to maintain consistency.

Key Guidelines:

What to Type:

• Function parameters: def func(param: ConcreteType) -> ReturnType:
• Return types: -> Response, -> None, -> list[str]
• Generic types where needed: dict[str, str], list[SomeModel]
• Class method signatures: def method(self, param: Type) -> ReturnType:

What NOT to Type (unless mypy explicitly requires it):

• Function local variables: retry_count = 6, data = {"key": "value"}, response = self.api_call()
• Class attributes with obvious values: api_name = 'api-name' (not api_name: str = 'api-name')
• Variables where type is inferred: matching_models_list = [] (not matching_models_list: list[Type] = [])
• Exception classes unless they have custom behavior beyond standard Python exceptions
• Simple dataclasses that already have field type annotations

Type Improvement Priorities:

1. Replace Any with concrete types when you can determine the actual type from context, imports, or usage
2. Verify existing type annotations are accurate and not overly broad
3. Use more specific types where possible (e.g., dict[str, str] instead of dict[str, Any] if the values are always strings)
4. Use modern Python syntax: use Type1 | Type2 instead of Union[Type1, Type2]
5. Preserve existing good typing: Don't change well-typed code just for the sake of change
6. Only define custom types if necessary: Only if it's currently untyped or wrongly typed. Don't add custom types just to copy my_project/my_app
7. It is okay not do to anything: If current codes are already typed correctly, it is okay not to change anything

Code Style Requirements:

• Preserve all existing comments: Never remove or modify existing comments - they often contain important context
• Add "TODO: please check this type" comments only on lines where you are genuinely uncertain about the type
• Use direct type references: use MyClass not 'MyClass'. Use forward reference only if it's necessary
• Follow existing patterns: If a file already has a typing style, maintain consistency

What to Avoid:

• Adding types to obvious assignments: self.logger = logger doesn't need : logging.Logger
• Over-typing simple operations: result = [] doesn't need result: list[Item] = []
• Modifying working code that already has proper typing
• Adding unnecessary complexity to exception classes or simple data structures

Verification Process:

• Run mypy first to see what it actually requires
• Only add annotations for mypy errors, not for "nice to have" typing
• If mypy passes without a type annotation, don't add it
• Focus on fixing actual mypy failures, not improving already-working code

Verification: Ensure these tools pass, you might want to activate the virtual env in .venv first:

• uv run flake8
• uv run black --check --diff .
• uv run mypy my_project/my_app
• uv run isort --check --diff .
