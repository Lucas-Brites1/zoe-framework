from zoe import App, Server, Router, Handler, Model, Field, Response, HttpCode, Route
from zoe import NotNull, Length, Range, Email, Logger, Limiter, Container, Box, HttpMethod


test_route = Route(endpoint="/teste_container", method=HttpMethod.GET, handler=Handler())
Container.provide(Box(test_route))


class CreateUserDto(Model):
    login: str = Field(NotNull(), Length(min=3, max=50))
    password: str = Field(NotNull(), Length(min=8))
    email: str = Field(NotNull(), Email())
    age: int = Field(NotNull(), Range(min=18, max=120))

class CreatePostDto(Model):
    title: str = Field(NotNull(), Length(min=5, max=100))
    content: str = Field(NotNull(), Length(min=10))

_users = {}
_posts = {}

class CreateUserHandler(Handler):
    def handle(self, body: CreateUserDto) -> Response:
        user_id = str(len(_users) + 1)
        _users[user_id] = body
        return Response(HttpCode.CREATED, body={"id": user_id, "user": body})

class GetUserHandler(Handler):
    def handle(self) -> Response:
        user_id = self.request.path_params.user_id
        user = _users.get(user_id)
        if not user:
            return Response(HttpCode.NOT_FOUND, body={"error": "User not found"})
        return Response(HttpCode.OK, body={"user": user})

class ListUsersHandler(Handler):
    def handle(self) -> Response:
        page = int(self.request.query_params.page or 1)
        limit = int(self.request.query_params.limit or 10)
        users = list(_users.values())
        start = (page - 1) * limit
        return Response(HttpCode.OK, body={
            "users": users[start:start + limit],
            "total": len(users),
            "page": page,
            "limit": limit
        })

class DeleteUserHandler(Handler):
    def handle(self) -> Response:
        user_id = self.request.path_params.user_id
        if user_id not in _users:
            return Response(HttpCode.NOT_FOUND, body={"error": "User not found"})
        del _users[user_id]
        return Response(HttpCode.NO_CONTENT)

class CreatePostHandler(Handler):
    def handle(self, body: CreatePostDto) -> Response:
        user_id = self.request.path_params.user_id
        if user_id not in _users:
            return Response(HttpCode.NOT_FOUND, body={"error": "User not found"})
        post_id = str(len(_posts) + 1)
        _posts[post_id] = {"author": user_id, **body.to_dict()}
        return Response(HttpCode.CREATED, body={"id": post_id, "post": _posts[post_id]})

class ListPostsHandler(Handler):
    def handle(self) -> Response:
        user_id = self.request.path_params.user_id
        user_posts = {k: v for k, v in _posts.items() if v["author"] == user_id}
        return Response(HttpCode.OK, body={"posts": user_posts, "total": len(user_posts)})

app: App = App()

if __name__ == "__main__":
    user_router = Router("/users")
    user_router\
        .POST("", CreateUserHandler())\
        .GET("", ListUsersHandler())\
        .GET("/{user_id}", GetUserHandler())\
        .DELETE("/{user_id}", DeleteUserHandler())\
        .POST("/{user_id}/posts", CreatePostHandler())\
        .GET("/{user_id}/posts", ListPostsHandler())

    app.use(Logger("CRUD-Test", verbose=True))\
       .use(Limiter())\
       .use(user_router)

    Server(app).run()
