# This file contains code that is largely copied from
# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject

from ..proxies import db_session


def unique_cache(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj


def unique_constructor(hashfunc, queryfunc):
    def decorate(cls):
        def _null_init(self, *arg, **kw):
            pass

        def __new__(cls, bases, *arg, **kw):
            # no-op __new__(), called
            # by the loading procedure
            if not arg and not kw:
                return object.__new__(cls)

            session = db_session()

            def constructor(*arg, **kw):
                obj = object.__new__(cls)
                obj._init(*arg, **kw)
                return obj

            return unique_cache(
                session,
                cls,
                hashfunc,
                queryfunc,
                constructor,
                arg, kw
            )

        # note: cls must be already mapped for this part to work
        cls._init = cls.__init__
        cls.__init__ = _null_init
        cls.__new__ = classmethod(__new__)
        return cls

    return decorate
