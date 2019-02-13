from alembic import util
from alembic.util import sqla_compat
from . import exclusions

if util.sqla_094:
    from sqlalchemy.testing.requirements import Requirements
else:

    class Requirements(object):
        pass


class SuiteRequirements(Requirements):
    @property
    def schemas(self):
        """Target database must support external schemas, and have one
        named 'test_schema'."""

        return exclusions.open()

    @property
    def unique_constraint_reflection(self):
        def doesnt_have_check_uq_constraints(config):
            from sqlalchemy import inspect

            # temporary
            if config.db.name == "oracle":
                return True

            insp = inspect(config.db)
            try:
                insp.get_unique_constraints("x")
            except NotImplementedError:
                return True
            except TypeError:
                return True
            except Exception:
                pass
            return False

        return exclusions.skip_if(doesnt_have_check_uq_constraints)

    @property
    def foreign_key_match(self):
        return exclusions.open()

    @property
    def check_constraints_w_enforcement(self):
        """Target database must support check constraints
        and also enforce them."""

        return exclusions.open()

    @property
    def reflects_pk_names(self):
        return exclusions.closed()

    @property
    def reflects_fk_options(self):
        return exclusions.closed()

    @property
    def fail_before_sqla_100(self):
        return exclusions.fails_if(
            lambda config: not util.sqla_100,
            "SQLAlchemy 1.0.0 or greater required",
        )

    @property
    def fail_before_sqla_1010(self):
        return exclusions.fails_if(
            lambda config: not util.sqla_1010,
            "SQLAlchemy 1.0.10 or greater required",
        )

    @property
    def fail_before_sqla_099(self):
        return exclusions.fails_if(
            lambda config: not util.sqla_099,
            "SQLAlchemy 0.9.9 or greater required",
        )

    @property
    def fail_before_sqla_110(self):
        return exclusions.fails_if(
            lambda config: not util.sqla_110,
            "SQLAlchemy 1.1.0 or greater required",
        )

    @property
    def sqlalchemy_092(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_092,
            "SQLAlchemy 0.9.2 or greater required",
        )

    @property
    def sqlalchemy_094(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_094,
            "SQLAlchemy 0.9.4 or greater required",
        )

    @property
    def sqlalchemy_099(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_099,
            "SQLAlchemy 0.9.9 or greater required",
        )

    @property
    def sqlalchemy_100(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_100,
            "SQLAlchemy 1.0.0 or greater required",
        )

    @property
    def sqlalchemy_1014(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_1014,
            "SQLAlchemy 1.0.14 or greater required",
        )

    @property
    def sqlalchemy_1115(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_1115,
            "SQLAlchemy 1.1.15 or greater required",
        )

    @property
    def sqlalchemy_110(self):
        return exclusions.skip_if(
            lambda config: not util.sqla_110,
            "SQLAlchemy 1.1.0 or greater required",
        )

    @property
    def sqlalchemy_issue_4436(self):
        def check(config):
            vers = sqla_compat._vers

            if vers == (1, 3, 0, 'b1'):
                return True
            elif vers >= (1, 2, 16):
                return False
            else:
                return True

        return exclusions.skip_if(
            check,
            "SQLAlchemy 1.2.16, 1.3.0b2 or greater required",
        )

    @property
    def pep3147(self):

        return exclusions.only_if(lambda config: util.compat.has_pep3147())

    @property
    def comments(self):
        return exclusions.only_if(
            lambda config: sqla_compat._dialect_supports_comments(
                config.db.dialect
            )
        )

    @property
    def comments_api(self):
        return exclusions.only_if(lambda config: util.sqla_120)
