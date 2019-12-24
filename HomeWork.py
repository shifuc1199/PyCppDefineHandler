def find_not_space(str, start_pos): #找到第一个不是空格的字符
    for str_ in range(start_pos, len(str)):
        if str[str_] != ' ':
            return str_

def tuple_to_list(data):  # 元组递归转list
    for str_ in range(0,len(data)):
        if type(data[str_]) == tuple:
            data[str_] = list(data[str_])
            tuple_to_list(data[str_])
    return data


def list_to_tuple(data): # list递归转元组
    for str_ in range(0,len(data)):
        if type(data[str_]) == list:
            list_to_tuple(data[str_])
            data[str_] = tuple(data[str_])   
    return data

def get_result_str_from_lst(lst): # 返回写入文件的元组字符串(不能直接str 会出错)
    temp_str = ''
    for index in range(0,len(lst)):
        if type(lst[index]) == list:
            temp_str += "{"+get_result_str_from_lst(lst[index])+"}"      
        else:
            temp_str += lst[index]
        if index <len(lst)-1:
            temp_str+=","
    return temp_str

def update_c_lst(data): # 递归更新 要写入cpp文件的聚合 把元组里所有的数据类型转为cpp对应的类型 并转为聚合
    for str_ in data:
        if type(str_) == list:
            update_c_lst(str_)
        data[data.index(str_)] = change_to_c(str_)
    return data
    
def update_py_lst(data):  # 递归更新 tuple 把所有字符串转义字符进行处理 （要存进字典）
    for str_ in data:
        if type(str_) == list:
            update_py_lst(str_)
        if type(str_) == str:
            data[data.index(str_)] = str_.decode("string-escape")
    return data

def is_macro_commond(data): # 判断是不是宏指令
    return data == '#define' or data == '#ifdef' or data == '#undef' or data == '#endif' or data == '#else' or data == 'ifndef'

def get_tuple(data,index):  # 递归 聚合转tuple类型 并处理其中的数据
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

def change_to_python(data): # 把数据 根据对应的类型 转为相应的PYTHON对应的类型
    data = data.strip()
    if data[0] == '{' and data[-1]=='}': # 聚合类型  转 tuple
        index = 0
        temp_str = ''
        while index < len(data):
            if data[index] == '"':
                temp_str += data[index]
                index += 1
                while data[index] != '"' or data[index-1] =='\\':
                    temp_str += data[index]
                    index += 1
                    if index >= len(data):
                        break
                else:
                    temp_str += data[index]
                    index += 1
            elif data[index] =="'"or data[index-1] =='\\':
                temp_str += data[index]
                index += 1
                while data[index] != "'":
                    temp_str += data[index]
                    index += 1
                    if index >= len(data):
                        break
                else:
                    temp_str += data[index]
                    index += 1
            elif data[index].isspace():
                index += 1
            else:
                temp_str += data[index]
                index += 1
        return (get_tuple(temp_str,0)[0][-1])
    if data.find('"')== 0 or (data.find('"')== 1 and data[0]=='L'): #字符串类型 要处理字符串拼接 和宽字符串
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
            for str_ in range(0,len(start_pos_lst)):
                result += data[0:start_pos_lst[str_]]+data[end_pos_lst[str_]+1:len(data)]
            return result
    if '0x' in data or '0X' in data: #16进制的类型 要注意处理后缀
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
    if data[0] == "'" and data[-1]== "'": #字符类型
        data = data[1:-1]
        try:
            t =ord(data.decode("string-escape"))
        except:
            pass
        else:
            return t
    if '.' in data: # float类型 要注意后缀 和e
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
    if data.strip('-')[0] == '0' and len(data)>1: #八进制
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
    if data.lstrip('-').isdigit(): #判断是不是整数
            try:
                t = int(data)        
            except:
                pass
            else:
                return t
    return data

def change_to_c(data): # 转换为存入cpp文件中应该对应的数据类型
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

def clear_note(temp_str): #删除代码中所有注释 注意：跳过字符串中的// 和/*
    is_note = False
    str_lst = []
    for ss in temp_str:
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
    return str_lst

def get_data(str_lst):  #删除多余的空格和\t 按空格分割得到正确的数据列表
    result_dict = []
    for str_ in str_lst:
        if str_ != '':
            temp_str = ''
            index = 0
            while index < len(str_):
                if str_[index] == '"':
                    temp_str += str_[index]
                    index += 1
                    while str_[index] != '"'or str_[index-1] !='\\':
                        temp_str += str_[index]
                        index += 1
                        if index >= len(str_):
                            break
                    else:
                        temp_str += str_[index]
                        index += 1
                elif str_[index] == "'":
                    temp_str += str_[index]
                    index += 1
                    while index < len(str_) and (str_[index] != '"'or str_[index-1] !='\\'):
                        temp_str += str_[index]
                        index += 1
                        if index >= len(str_):
                            break
                    else:
                        if index >= len(str_):
                            break
                        temp_str += str_[index]
                        index += 1
                elif str_[index].isspace() or str_[index] =='\t':
                    temp_str += ' '
                    index += 1
                    while index < len(str_) and str_[index] == ' ':
                        index += 1
                        if index >= len(str_):
                            break
                else:
                    temp_str += str_[index]
                    index += 1
            start_pos = temp_str.find('#')
            end_pos = find_not_space(temp_str, start_pos + 1)
            temp_str = temp_str[start_pos] + temp_str[end_pos:]
            for j in temp_str.split(' ', 2):
                if j != '':
                    result_dict.append(j)
    return result_dict

class PyMacroParser:

    def __init__(self):
        self.predefine_dict = {}
        self.define_dict = {}
        self.str_lst = []

    def load(self, f):
        try:
            file_ = open(f, 'r')
            str_ = file_.read()
        except:
            return
        file_.close()
        split_str = str_.split('\n')
        self.str_lst = get_data(clear_note(split_str))

    def update(self):
        index = 0
        self.define_dict = {}
        for k, v in self.predefine_dict.items():
            if v == None:
                self.define_dict[k] = None
            else:
                self.define_dict[k] =  change_to_python(v)
        while index < len(self.str_lst):
            commond = self.str_lst[index]
            if commond == "#ifndef":
                index += 1
                identifier = self.str_lst[index]
                if identifier in self.define_dict.keys():
                    index = self.get_index(index)
                else:
                    index += 1
            elif commond == "#ifdef":
                index += 1
                identifier = self.str_lst[index]
                if identifier not in self.define_dict.keys():
                    index = self.get_index(index)
                else:
                    index += 1
            elif commond == "#else":
                index += 1
                index = self.get_index(index)
            elif commond == '#define':
                if index == len(self.str_lst) - 1 or self.str_lst[index + 1] == '#define' :
                    index += 1
                    continue
                if index + 2 < len(self.str_lst) and not is_macro_commond(self.str_lst[index + 2]):
                    token_stringopt  = self.str_lst[index + 2]
                    identifier  = self.str_lst[index + 1]
                    self.define_dict[identifier] = change_to_python(token_stringopt)
                    index += 3
                else:
                    identifier  = self.str_lst[index + 1]
                    self.define_dict[identifier] = None
                    index += 2
            elif commond == "#undef":
                index += 1
                identifier = self.str_lst[index]
                if identifier in self.define_dict:
                    self.define_dict.pop(identifier)
                index += 1
            else:
                index += 1

    def get_index(self, index): #处理分支 
        if_count = 1
        else_count = 0
        while index < len(self.str_lst):
            commond = self.str_lst[index]
            if commond == "#ifndef" or commond == "#ifdef":
                if_count += 1
            elif commond == "#else":
                else_count += 1
                if else_count == if_count == 1:
                    return index + 1
            elif commond == "#endif":
                if_count -= 1
                if else_count > 0: else_count -= 1
                if if_count == else_count == 0:
                    return index + 1
            index += 1

    def preDefine(self, s):
        self.predefine_dict.clear()
        lst = s.split(';')
        for str_ in lst:
            if str_ == '':
                continue
            self.predefine_dict[str_] = None

    def dumpDict(self):
        self.update()
        copy_dict = {}
        for index in self.define_dict:
            copy_dict [index]= self.define_dict[index]
            if type(copy_dict [index]) == str:
               copy_dict [index] =copy_dict [index].decode('string-escape')
            if type(copy_dict [index]) == tuple:
                l = copy_dict [index]
                new_lst = tuple_to_list(list(l))
                right_lst = update_py_lst(new_lst)
                right_tuple = list_to_tuple(right_lst)
                copy_dict[index]= tuple(right_tuple)
        return copy_dict

    def dump(self, f):
        self.update()
        amount = 0
        temp_str = ''
        for k, v in self.define_dict.items():
            amount += 1
            if v == None:
                temp_str += '#define ' + k
            else:
                if type(v) == tuple :
                    new_lst = tuple_to_list(list(v))
                    right_lst = update_c_lst(new_lst)
                    result_s = get_result_str_from_lst(right_lst)
                    temp_str += '#define ' + k + " " +"{"+result_s+"}"
                else:
                    temp_str += '#define ' + k + " " +change_to_c(v)
            if amount < len(self.define_dict):
                temp_str += '\n'
        try:
            with open(f, 'w')as f:
                f.write(temp_str)
        except IOError, arg:
            raise IOError(arg)