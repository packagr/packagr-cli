from packagr.commands.base import Command


class CreateToken(Command):
    """
    Create an access token for a specific package and user

    create-token
        {package : The name of the package for which to create an access token}
        {email : The email address of the user to create the token for}
        {--w|write-access : Whether to give the user write access. By default, read-only access is granted}
    """

    def handle(self) -> None:
        package_name = self.argument('package')
        email = self.argument('email')
        write_access = self.option('write-access')

        self.line(f'Attempting to create access token for user {email} and package {package_name}...')

        package = self.retrieve_package(package_name)
        user = self.retrieve_user(email)

        if package:
            if user:
                if self.create_access_token(package, user, write_access=write_access):
                    self.line('<info>Access token created</info>')
            else:
                self.line('<error>Cannot find a user with that email</error>')

        else:
            self.line('<error>Cannot find a package with that name</error>')


class DeleteToken(Command):
    """
    Delete an access token for a specific package and user

    delete-token
        {package : The name of the package for which to delete an access token}
        {email : The email address of the user whose access token is to be deleted}
    """

    def handle(self) -> None:
        package_name = self.argument('package')
        email = self.argument('email')

        self.line(f'Attempting to delete access token for user {email} and package {package_name}...')

        package = self.retrieve_package(package_name)

        if package:
            user = self.retrieve_user(email)

            if user:
                token = self.retrieve_token(package, user)

                if token:
                    if self.delete_access_token(token):
                        self.line('<info>Access token deleted</info>')
                else:
                    self.line('<error>Cannot delete access token for this package/user combination</error>')
            else:
                self.line('<error>Cannot find a user with that email</error>')

        else:
            self.line('<error>Cannot find a package with that name</error>')
