from . import data_definition

__doc__ = "Message part"

GS = '\x1d'
RS = '\x1e'

class Data:
    "A data entry"
    def __init__(self, group, definition, value):
        self.group = group
        self.definition = definition
        self.value = value

class VariableData(Data):
    "A variable length data entry"
    def __init__(self, group, definition, value, complete = True):
        super().__init__(group, definition, value)
        self.complete = complete
    
class FixedData(Data):
    "A fixed length data entry"
    pass

class Message:
    "A message"
    def __init__(self, perimeter_id, dataset):
        self.perimeter_id = perimeter_id
        self.dataset = list(dataset)
        
class C40Message(Message):
    "A C40 message"
    def encode(self, max_length = None):
        raise NotImplementedError()

    @classmethod
    def from_code(cls, perimeter_id, code):
        """
        Load a message from a C40 code string, for a given perimeter ID.
        """
        self = cls(perimeter_id, [])
        while code:
            data, code = self.code_extract(code)
            self.dataset.append(data)
        return self

    @classmethod
    def fixed_parse(cls, group, definition, code):
        """
        Parse a fixed size data item in the stream
        """
        value = definition.encoding.parse(code[2:2 + definition.fixed])
        data = FixedData(group, definition, value)
        if code[2 + definition.fixed : 2 + definition.fixed + 1] == GS:
            return data, code[2 + definition.fixed + 1 : ]
        return data, code[2 + definition.fixed : ]

    @classmethod
    def variable_parse(cls, group, definition, code):
        """
        Parse a variable size data item in the stream
        """
        try:
            end_pos = code.index(RS)
            complete = False
        except:
            complete = True
            try:
                end_pos = code.index(GS)
            except:
                end_pos = None

        if definition.encoding.size_max is not None \
           and (end_pos is None
                or end_pos > 2 + definition.encoding.size_max):
            end_pos = definition.encoding.size_max + 1
            complete = True
                
        value = definition.encoding.parse(code[2:end_pos])
        data = FixedData(group, definition, value)
        if end_pos is None:
            return data, ''
        else:
            return data, code[end_pos + 1:]

    def code_extract(self, code):
        """
        Parse next data item in the stream
        """
        group, definition = data_definition.c40.datatype_get(self.perimeter_id, code[:2])
        if definition.fixed is not None:
            return self.fixed_parse(group, definition, code)
        return self.variable_parse(group, definition, code)

