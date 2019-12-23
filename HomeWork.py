def replaceAll(old, new, str):
    while str.find(old) > -1:
        str = str.replace(old, new)
    return str

def find_not_space(str, start_pos):
    for i in range(start_pos, len(str)):
        if str[i] != ' ':
            return i

def find_f_index(_str):
    index_lst = []
    for i in range(0, len(_str)):
        if _str[i] == 'f':
            index_lst.append(i)
    return index_lst

def is_macro_commond(data):
    return data == '#define' or data == '#ifdef' or data == '#undef' or data == '#endif' or data == '#else' or data == 'ifndef'

def get_tuple(data,index):
    lst = []
    while index < len(data):
        if data[index] == '{':
            index += 1
            t,index = get_tuple(data,index)
            lst.append(t)
        elif data[index] == '}':
            index += 1
            return tuple(lst),index
        else:
            startpos = index
            while index < len(data):
                if data[index] == ',':
                    if startpos == index:
                        index += 1
                        break
                    lst.append(change_to_python(data[startpos:index]))
                    index += 1
                    break
                elif data[index] == '}':
                    lst.append(change_to_python(data[startpos:index]))
                    break
                elif data[index] == '"':
                    index += 1
                    if index >= len(data):
                        lst.append(change_to_python(data[startpos:index]))
                        break
                    while data[index] != '"':
                        index += 1
                        if index >= len(data):
                            lst.append(change_to_python(data[startpos:index]))
                            break
                    else:
                        index+=1
                else:
                    index +=1
    else:
        return tuple(lst),index

def change_to_python(data):
    data = data.strip()
    if data[0] == '{' and data[-1]=='}':
        index = 0
        result_str = ''
        while index < len(data):
            if data[index] == '"':
                result_str += data[index]
                index += 1
                while data[index] != '"' or data[index-1] =='\\':
                    result_str += data[index]
                    index += 1
                    if index >= len(data):
                        break
                else:
                    result_str += data[index]
                    index += 1
            elif data[index] =="'"or data[index-1] =='\\':
                result_str += data[index]
                index += 1
                while data[index] != "'":
                    result_str += data[index]
                    index += 1
                    if index >= len(data):
                        break
                else:
                    result_str += data[index]
                    index += 1
            elif data[index].isspace():
                index += 1
            else:
                result_str += data[index]
                index += 1
        return (get_tuple(result_str,0)[0][-1])
    if data.find('"')== 0 or (data.find('"')== 1 and data[0]=='L'):
        if data[0] == 'L':
            data = data.replace('"', "")
            return unicode(data[1:])
        data = data.strip('"')
        index = 0
        start_pos_lst = []
        end_pos_lst = []
        while index < len(data):
            if data[index] == '"':
                start_pos_lst.append(index)
                if index +1 <len(data):
                    index += 1
                    while data[index] != '"':
                        if data[index] == ' ' or data[index] == '\t':
                            index += 1
                        else:
                            start_pos_lst.remove(start_pos_lst[-1])
                            break
                    else:
                        end_pos_lst.append(index)
            else:
                index += 1
        if len(start_pos_lst) ==0 and len(end_pos_lst) ==0:
                return data
        else:
            result = ''
            for i in range(0,len(start_pos_lst)):
                result += data[0:start_pos_lst[i]]+data[end_pos_lst[i]+1:len(data)]
            return result
    if '0x' in data or '0X' in data:
        try:
            data = data.rstrip('l')
            data = data.rstrip('u')
            data = data.rstrip('U')
            data = data.rstrip('L')
            t = int(str(data), 16)
        except:
            pass
        else:
            return t  
    if data[0] == "'" and data[-1]== "'":
        data = data[1:-1]
        try:
            t =ord(data.decode("string-escape"))
        except:
            pass
        else:
            return t
    if '.' in data:
        if data[-1].lower() == 'f' or data[-1].lower() == 'l':
            try:
                t = float(data[0:-1])
            except:
                pass
            else:
                return t
        else:
            try:
                t = float(data)
            except:
                pass
            else:
                return t
    else:
        if 'e' in data or 'E' in data:
            try:
                t = float(data)
            except:
                pass
            else:
                return t
    if data.strip('-')[0] == '0' and len(data)>1:
        try:
            t = int(data,8)
        except:
            pass
        else:
            return t
    if data == 'false':
        return False
    if data == 'true':
        return True
    data = data.replace('u','')
    data = data.replace('l','')
    data = data.replace('U','')
    data = data.replace('L','')
    if data.lstrip('-').isdigit():
            try:
                t = int(data)        
            except:
                pass
            else:
                return t
    return data

def change_to_c(data):
    if type(data) == unicode:
        return 'L' + '"' + data + '"'
    if type(data) == str:
        return '"' + data + '"'
    if type(data) == bool:
        if data:
            return 'true'
        else:
            return 'false'
    if type(data) == list:
        return data
    return str(data)

class PyMacroParser:

    def __init__(self):
        self.predefine_dict = {}
        self.define_dict = {}
        self.result_str = ''
        self.str_lst = []

    def load(self, f):
        try:
            file_ = open(f, 'r')
            str_ = file_.read()
        except:
            return
        file_.close()
        p = str_.split('\n')
        is_note = False
        str_lst = []
        for ss in p:
            startp = []
            endp = []
            index = 0
            while index < len(ss) :
                if is_note:
                    startp.append(0)
                    while ss[index] != '*' or ss[index + 1] != '/':
                        index += 1
                        if index >= len(ss) - 1:
                            endp.append(len(ss))
                            break
                    else:
                        endp.append(index+1)
                        is_note = False
                        index+=2
                        if index>=len(ss):
                            break
                if ss[index] == '"':
                    index += 1
                    while index < len(ss) and ss[index] !='"':
                        index += 1
                    else:
                        index += 1
                        if index>=len(ss):
                            break
                elif ss[index] == "'":
                    index += 1
                    while index < len(ss) and ss[index] != "'":
                        index += 1
                    else:
                        index += 1
                        if index>=len(ss):
                            break
                elif index < len(ss)-1 and ss[index] == '/' and ss[index+1] == '*':
                    startp .append(index)
                    index += 2
                    if index >= len(ss) - 1:
                        endp.append(len(ss))
                        is_note = True
                        break
                    while  ss[index] !='*' or ss[index+1] !='/':
                        index += 1
                        if index>=len(ss)-1:
                            endp.append(len(ss))
                            is_note = True
                            index = len(ss)
                            break
                    else:
                        endp.append(index+1)
                        index += 2
                elif index < len(ss)-1 and ss[index] == '/' and ss[index+1] == '/':
                    startp.append(index)
                    endp.append(len(ss))
                    break
                else:
                    index += 1
            temp_str = ''
            if len(startp)==0 and len(endp) ==0:
                str_lst.append(ss)
            else:
                if startp[0] !=0:
                    temp_str += ss[0:startp[0]]+' '
                for index in range(0,len(startp)):
                    if index == len(startp)-1 :
                        if endp[index] != len(ss):
                            temp_str += ss[endp[index]+1:len(ss)]+' '
                        else:
                            pass
                    else:
                        temp_str += ss[endp[index]+1:startp[index+1]]+' '
                if temp_str !='':
                    str_lst.append(temp_str)
        for i in str_lst:
            if i != '':
                p = ''
                temp = 0
                while temp < len(i):
                    if i[temp] == '"':
                        p += i[temp]
                        temp += 1
                        while i[temp] != '"'or i[temp-1] !='\\':
                            p += i[temp]
                            temp += 1
                            if temp >= len(i):
                                break
                        else:
                            p += i[temp]
                            temp += 1
                    elif i[temp] == "'":
                        p += i[temp]
                        temp += 1
                        while temp < len(i) and (i[temp] != '"'or i[temp-1] !='\\'):
                            p += i[temp]
                            temp += 1
                            if temp >= len(i):
                                break
                        else:
                            if temp >= len(i):
                                break
                            p += i[temp]
                            temp += 1
                    elif i[temp].isspace() or i[temp] =='\t':
                        p += ' '
                        temp += 1
                        while temp < len(i) and i[temp] == ' ':
                            temp += 1
                            if temp >= len(i):
                                break
                    else:
                        p += i[temp]
                        temp += 1
                start_pos = p.find('#')
                end_pos = find_not_space(p, start_pos + 1)
                p = p[start_pos] + p[end_pos:]
                for j in p.split(' ', 2):
                    if j != '':
                        self.str_lst.append(j)

    def update(self):
        index = 0
        self.final_lst = []
        self.result_str = ''
        self.define_dict = {}
        for k, v in self.predefine_dict.items():
            if v == None:
                self.define_dict[k] = None
            else:
                self.define_dict[k] =  change_to_python(v)
        while index < len(self.str_lst):
            if self.str_lst[index] == "#ifndef":
                index += 1
                if self.str_lst[index] in self.define_dict.keys():
                    index = self.get_index(index)
                else:
                    index += 1
            elif self.str_lst[index] == "#ifdef":
                index += 1
                if self.str_lst[index] not in self.define_dict.keys():
                    index = self.get_index(index)
                else:
                    index += 1
            elif self.str_lst[index] == "#else":
                index += 1
                index = self.get_index(index)
            elif self.str_lst[index] == '#define':
                if index == len(self.str_lst) - 1 or self.str_lst[index + 1] == '#define' :
                    index += 1
                    continue
                if index + 2 < len(self.str_lst) and not is_macro_commond(self.str_lst[index + 2]):
                    self.define_dict[self.str_lst[index + 1]] = change_to_python(self.str_lst[index + 2])

                    index += 3
                else:
                    self.define_dict[self.str_lst[index + 1]] = None
                    index += 2
            elif self.str_lst[index] == "#undef":
                index += 1
                if self.str_lst[index] in self.define_dict:
                    self.define_dict.pop(self.str_lst[index])
                index += 1
            else:
                index += 1

    def get_index(self, index):
        if_count = 1
        else_count = 0
        while index < len(self.str_lst):
            if self.str_lst[index] == "#ifndef" or self.str_lst[index] == "#ifdef":
                if_count += 1
            elif self.str_lst[index] == "#else":
                else_count += 1
                if else_count == if_count == 1:
                    return index + 1
            elif self.str_lst[index] == "#endif":
                if_count -= 1
                if else_count > 0: else_count -= 1
                if if_count == else_count == 0:
                    return index + 1
            index += 1

    def preDefine(self, s):
        self.predefine_dict.clear()
        lst = s.split(';')
        for i in lst:
            if i == '':
                continue
            self.predefine_dict[i] = None

    def dumpDict(self):
        self.update()
        copy_dict = {}
        for temp in self.define_dict:
            copy_dict [temp]= self.define_dict[temp]
            if type(copy_dict [temp]) == str:
               copy_dict [temp] =copy_dict [temp].decode('string-escape')
            if type(copy_dict [temp]) == tuple:
                l = copy_dict [temp]
                new_lst = change_tuple_to_list(list(l))
                right_lst = update_lst(new_lst)
                right_tuple = change_list_to_tuple(right_lst)
                copy_dict[temp]= tuple(right_tuple)

        return copy_dict

    def dump(self, f):
        self.update()
        amount = 0
        for k, v in self.define_dict.items():
            amount += 1
            if v == None:
                self.result_str += '#define ' + k
            else:
                if type(v) == tuple :
                    new_lst = change_tuple_to_list(list(v))
                    right_lst = update_c_lst(new_lst)
                    result_s = get_result_str_from_lst(right_lst)
                    self.result_str += '#define ' + k + " " +"{"+result_s+"}"
                else:
                    self.result_str += '#define ' + k + " " +change_to_c(v)
            if amount < len(self.define_dict):
                self.result_str += '\n'
        try:
            with open(f, 'w')as f:
                f.write(self.result_str)
        except IOError, arg:
            raise IOError(arg)


def change_tuple_to_list(data):
    for i in range(0,len(data)):
        if type(data[i]) == tuple:
            data[i] = list(data[i])
            change_tuple_to_list(data[i])
    return data

def get_result_str_from_lst(lst):
    result_str = ''
    for index in range(0,len(lst)):
        if type(lst[index]) == list:
            result_str += "{"+get_result_str_from_lst(lst[index])+"}"      
        else:
            result_str += lst[index]
        if index <len(lst)-1:
            result_str+=","
    return result_str

def update_c_lst(data):
    for i in data:
        if type(i) == list:
            update_c_lst(i)
        data[data.index(i)] = change_to_c(i)
    return data
    
def update_lst(data):
    for i in data:
        if type(i) == list:
            update_lst(i)
        if type(i) == str:
            data[data.index(i)] = i.decode("string-escape")
    return data

def change_list_to_tuple(data):
    for i in range(0,len(data)):
        if type(data[i]) == list:
            change_list_to_tuple(data[i])
            data[i] = tuple(data[i])   
    return data
