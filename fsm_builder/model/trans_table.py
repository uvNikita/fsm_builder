import json
from operator import itemgetter

from gi.repository import Gtk

from ..util import underscripted


class Implicant(object):
    def __init__(self, values):
        self.values = values

    def __repr__(self):
        pass

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)


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
                impl_str += name
            impls_str.append(impl_str)
        func_str = ' ∨ '.join(impls_str) or '0'
        return "{f} = {value}".format(f=self.name, value=func_str)


class TransTable(object):
    def __init__(self, table_holder, triggers_holder):
        self.table_view = table_holder
        self.triggers_view = triggers_holder
        self.table = []

    def fill(self, table):
        self.table = table

    def clear(self):
        for column in self.table_view.get_columns():
            self.table_view.remove_column(column)

    def dump(self, fp):
        return json.dump(self.table, fp)

    def load(self, fp):
        return self.fill(json.load(fp))

    def _add_column(self, label, map_idx):
        column = Gtk.TreeViewColumn(label, Gtk.CellRendererText(), text=map_idx)
        self.table_view.append_column(column)

    def draw(self):
        self.draw_table()
        self.draw_funcs()

    def draw_funcs(self):
        def get_func(name, rows):
            args = []
            for q_id in range(len(rows[0]['from_code'])):
                args.append(underscripted('Q{}'.format(q_id)))
            for cond_id, value in sorted(rows[0]['cond'].items()):
                args.append(underscripted('X{}'.format(cond_id)))
            impls = []
            for row in rows:
                impl_vals = list(map(int, row['from_code'][:]))
                for cond_id, cond_val in sorted(row['cond'].items()):
                    if cond_val is None:
                        impl_vals.append(cond_val)
                    elif cond_val:
                        impl_vals.append(1)
                    else:
                        impl_vals.append(0)
                impls.append(Implicant(impl_vals))
            return Function(name, args, impls)

        funcs = []
        for trig_id in range(len(self.table[0]['from_code'])):
            j_ones = []
            k_ones = []
            for row in self.table:
                if row['trig'][trig_id][0]:
                    j_ones.append(row)
                if row['trig'][trig_id][1]:
                    k_ones.append(row)
            j_name = underscripted('J{} = '.format(trig_id))
            j_func = get_func(j_name, j_ones)
            funcs.append(j_func)

            k_name = underscripted('K{} = '.format(trig_id))
            k_func = get_func(k_name, k_ones)
            funcs.append(k_func)

        for ctrl_id in self.table[0]['ctrls']:
            ctrl_ones = [row for row in self.table if row['ctrls'][ctrl_id]]
            ctrl_name = underscripted('Y{} = '.format(ctrl_id))
            ctrl_func = get_func(ctrl_name, ctrl_ones)
            funcs.append(ctrl_func)

        buffer = self.triggers_view.get_buffer()
        buffer.set_text('\n'.join(map(str, funcs)))

    def draw_table(self):
        def _value_to_str(value):
            if value is None:
                return '-'
            elif value:
                return '1'
            else:
                return '0'

        self.clear()
        row = self.table[0]

        self._add_column('FS', 0)
        idx = 1

        for fc_id in range(len(row['from_code'])):
            label = underscripted('Q{}'.format(fc_id))
            self._add_column(label, idx)
            idx += 1

        self._add_column('', idx)
        idx += 1

        self._add_column('TS', idx)
        idx += 1

        for tc_id in range(len(row['to_code'])):
            label = underscripted('Q{}'.format(tc_id))
            self._add_column(label, idx)
            idx += 1

        self._add_column('', idx)
        idx += 1

        for cond_id in sorted(row['cond'].keys()):
            label = underscripted('X{}'.format(cond_id))
            self._add_column(label, idx)
            idx += 1

        self._add_column('', idx)
        idx += 1

        for ctrl_id in sorted(row['ctrls'].keys()):
            label = underscripted('Y{}'.format(ctrl_id))
            self._add_column(label, idx)
            idx += 1

        self._add_column('', idx)
        idx += 1

        for trig_id in range(len(row['trig'])):
            j_label = underscripted('J{}'.format(trig_id))
            self._add_column(j_label, idx)
            idx += 1

            k_label = underscripted('K{}'.format(trig_id))
            self._add_column(k_label, idx)
            idx += 1

            self._add_column('', idx)
            idx += 1

        store = Gtk.ListStore(*([str] * idx))

        for t_row in self.table:
            row = []
            row.append(t_row['from_name'])
            row.extend(t_row['from_code'])
            row.append('')
            row.append(t_row['to_name'])
            row.extend(t_row['to_code'])
            row.append('')
            cond_values = map(itemgetter(1), sorted(t_row['cond'].items()))
            ctrl_values = map(itemgetter(1), sorted(t_row['ctrls'].items()))
            row.extend(map(_value_to_str, cond_values))
            row.append('')
            row.extend(map(_value_to_str, ctrl_values))
            row.append('')
            for j_val, k_val in t_row['trig']:
                row.append(_value_to_str(j_val))
                row.append(_value_to_str(k_val))
                row.append('')
            store.append(row)
        self.table_view.set_model(store)

