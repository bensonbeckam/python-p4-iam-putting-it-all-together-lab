import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, User, Recipe


class TestRecipe:
    '''Tests for the Recipe model.'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            # Clean up DB
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create user to satisfy foreign key
            user = User(username="TestUser", _password_hash="somepassword")
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In"
                    " raptures building an bringing be. Elderly is detract"
                    " tedious assured private so to visited. Do travelling"
                    " companions contrasted it. Mistress strongly remember"
                    " up to. Ham him compass you proceed calling detract."
                    " Better of always missed we person mr. September"
                    " smallness northward situation few her certainty"
                    " something."
                ),
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe is not None
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            # also check the instructions length
            assert isinstance(new_recipe.instructions, str)
            assert len(new_recipe.instructions) >= 50

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Need a user
            user = User(username="UserWithoutRecipeTitle", _password_hash="pw")
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="a" * 60,
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()
                db.session.rollback()

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="ShortInstrUser", _password_hash="pw2")
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Generic Ham",
                instructions="idk lol",  # too short
                minutes_to_complete=10,
                user_id=user.id
            )

            with pytest.raises((IntegrityError, ValueError)):
                db.session.add(recipe)
                db.session.commit()
                db.session.rollback()


class TestUser:
    '''Tests for the User model.'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio=(
                    "Dame Elizabeth Rosemond Taylor DBE (February 27, 1932"
                    " - March 23, 2011) was a British-American actress. "
                    "She began her career as a child actress in the early"
                    " 1940s and was one of the most popular stars of "
                    "classical Hollywood cinema in the 1950s. She then"
                    " became the world's highest paid movie star in the "
                    "1960s, remaining a well-known public figure for the "
                    "rest of her life. In 1999, the American Film Institute"
                    " named her the seventh-greatest female screen legend "
                    "of Classic Hollywood cinema."
                )
            )
            user.password_hash = "whosafraidofvirginiawoolf"

            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter_by(username="Liz").first()

            assert created_user is not None
            assert created_user.username == "Liz"
            assert created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg"
            assert "Elizabeth Rosemond Taylor" in created_user.bio

            with pytest.raises(AttributeError):
                _ = created_user.password_hash

    def test_requires_username(self):
        '''requires each record to have a username.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user = User()

            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()
                db.session.rollback()

    def test_requires_unique_username(self):
        '''requires username to be unique.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user1 = User(username="Ben", _password_hash="hash1")
            db.session.add(user1)
            db.session.commit()

            user2 = User(username="Ben", _password_hash="hash2")

            with pytest.raises(IntegrityError):
                db.session.add(user2)
                db.session.commit()
                db.session.rollback()

    def test_has_list_of_recipes(self):
        '''has records with lists of recipes attached.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="Prabhdip", _password_hash="securepass")
            db.session.add(user)
            db.session.commit()

            recipe1 = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In"
                    " raptures building an bringing be. Elderly is detract"
                    " tedious assured private so to visited. Do travelling"
                    " companions contrasted it. Mistress strongly remember"
                    " up to. Ham him compass you proceed calling detract."
                    " Better of always missed we person mr. September"
                    " smallness northward situation few her certainty"
                    " something."
                ),
                minutes_to_complete=60,
                user_id=user.id
            )
            recipe2 = Recipe(
                title="Hasty Party Ham",
                instructions=(
                    "As am hastily invited settled at limited"
                    " civilly fortune me. Really spring in extent"
                    " an by. Judge but built gay party world. Of"
                    " so am he remember although required. Bachelor"
                    " unpacked be advanced at. Confined in declared"
                    " marianne is vicinity."
                ),
                minutes_to_complete=30,
                user_id=user.id
            )

            db.session.add_all([recipe1, recipe2])
            db.session.commit()

            assert user.id is not None
            assert recipe1.id is not None
            assert recipe2.id is not None

            # check that recipes are in the user.recipes relationship
            assert recipe1 in user.recipes
            assert recipe2 in user.recipes
