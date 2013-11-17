from ..util import underscripted


class Implicant(object):
    def __init__(self, values):
        self.values = tuple(values)

    def __repr__(self):
        return "Implicant({})".format(self.values)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def can_combine(self, other):
        was_diff = False
        for sv, ov in zip(self, other):
            if sv != ov:
                if not was_diff:
                    was_diff = True
                else:
                    return False
        return was_diff

    def is_include(self, other):
        for sv, ov in zip(self, other):
            if sv != ov and sv is not None:
                return False
        return True

    def combine(self, other):
        new_values = []
        for sv, ov in zip(self, other):
            if sv == ov:
                new_values.append(sv)
            else:
                new_values.append(None)
        return Implicant(new_values)


class Function(object):
    def __init__(self, name, args, impls):
        assert all(len(args) == len(impl) for impl in impls), "Arguments and implicants" \
                                                              "must be the same length"

        self.args = args
        self.impls = impls
        self.name = name

    def __repr__(self):
        impls_str = []
        for impl in self.impls:
            impl_str = ''
            for name, value in zip(self.args, impl):
                if value is None:
                    continue
                elif not value:
                    impl_str += '!'
                impl_str += underscripted(name)
            impls_str.append(impl_str)
        func_str = ' ∨ '.join(impls_str) or '1'
        return "{f} = {value}".format(f=underscripted(self.name), value=func_str)

    def minimize(self):
        def get_groups():
            def get_new_group(impls):
                group = []
                for idx, impl1 in enumerate(impls):
                    for impl2 in impls[idx + 1:]:
                        if impl1.can_combine(impl2):
                            group.append(impl1.combine(impl2))
                return tuple(group)

            if not self.impls:
                return []

            group = tuple(self.impls)
            groups = [group]
            while True:
                group = get_new_group(group)
                if group:
                    groups.append(group)
                else:
                    break
            return tuple(groups[::-1])

        def reduced(groups):
            if not groups:
                return ()
            base = groups[0][0]
            groups = (groups[0][1:],) + groups[1:]
            groups = (
                tuple(filter(lambda impl: not base.is_include(impl), group))
                for group in groups
            )
            return (base,) + reduced(tuple(filter(None, groups)))

        def minimized(impls, reduced_impls):
            res = set()
            for impl in impls:
                if any(rimpl.is_include(impl) for rimpl in res):
                    continue
                res.add(next(rimpl for rimpl in reduced_impls if rimpl.is_include(impl)))
            return tuple(res)

        reduced_impls = reduced(get_groups())
        min_impls = minimized(self.impls, reduced_impls)
        return Function(self.name, self.args, min_impls)


class Functions(object):
    def __init__(self, holder):
        self.holder = holder
        self.funcs = []

    def fill(self, funcs):
        self.funcs = funcs

    def draw(self):
        buffer = self.holder.get_buffer()
        buffer.set_text('\n'.join(map(str, self.funcs)))
