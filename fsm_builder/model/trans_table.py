import json
from operator import itemgetter

from gi.repository import Gtk

from ..util import underscripted


def _value_to_str(value):
    if value is None:
        return '-'
    elif value:
        return '1'
    else:
        return '0'


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
        self.draw_triggers()

    def draw_triggers(self):
        def get_func(rows):
            ors = []
            for row in rows:
                or_ = ''
                for qid, qval in enumerate(row['from_code']):
                    if qval == '0':
                        or_ += '!'
                    or_ += 'Q{}'.format(qid)
                for cond_id, cond_val in row['cond'].items():
                    if cond_val is None:
                        continue
                    elif not cond_val:
                        or_ += '!'
                    or_ += 'X{}'.format(cond_id)
                ors.append(or_)
            func = ' ∨ '.join(ors)
            return func
        funcs = []
        for trig_id in range(len(self.table[0]['from_code'])):
            j_ones = []
            k_ones = []
            for row in self.table:
                if row['trig'][trig_id][0]:
                    j_ones.append(row)
                if row['trig'][trig_id][1]:
                    k_ones.append(row)
            j_func = underscripted('J{} = '.format(trig_id))
            j_func += underscripted(get_func(j_ones)) or '0'

            k_func = underscripted('K{} = '.format(trig_id))
            k_func += underscripted(get_func(k_ones)) or '0'

            funcs.append(j_func + '\n' + k_func + '\n')
        buffer = self.triggers_view.get_buffer()
        buffer.set_text('\n'.join(funcs))

    def draw_table(self):
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

