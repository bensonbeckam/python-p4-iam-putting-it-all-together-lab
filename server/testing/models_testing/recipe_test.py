import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User  # Make sure User is imported


class TestRecipe:
    '''Tests for the Recipe model.'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():
            # Clean up existing data
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user
            user = User(username="TestUser", _password_hash="testpassword")
            db.session.add(user)
            db.session.commit()

            # Create a recipe associated with the user
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" +
                    """ raptures building an bringing be. Elderly is detract""" +
                    """ tedious assured private so to visited. Do travelling""" +
                    """ companions contrasted it. Mistress strongly remember""" +
                    """ up to. Ham him compass you proceed calling detract.""" +
                    """ Better of always missed we person mr. September""" +
                    """ smallness northward situation few her certainty""" +
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert isinstance(new_recipe.instructions, str)
            assert len(new_recipe.instructions) >= 50

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():
            # Clean up
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user
            user = User(username="NoTitleUser", _password_hash="abc123")
            db.session.add(user)
            db.session.commit()

            # Attempt to create recipe without a title
            recipe = Recipe(
                instructions="a" * 60,
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()
                db.session.rollback()  # Cleanup after failure

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters.'''

        with app.app_context():
            # Clean up
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user
            user = User(username="ShortInstructionsUser", _password_hash="pass123")
            db.session.add(user)
            db.session.commit()

            # Try short instructions (less than 50 chars)
            recipe = Recipe(
                title="Generic Ham",
                instructions="idk lol",
                minutes_to_complete=10,
                user_id=user.id
            )

            with pytest.raises((IntegrityError, ValueError)):
                db.session.add(recipe)
                db.session.commit()
                db.session.rollback()
