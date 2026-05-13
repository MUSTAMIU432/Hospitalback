import strawberry


@strawberry.type
class CoreQuery:
    @strawberry.field
    def health(self) -> str:
        return "ok"
