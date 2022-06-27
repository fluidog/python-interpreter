# 功能测试

# print('start test');

# 算数运算
3 + 5 * 6;
34 - 5 + 6;

# 条件分支（if）
if(1+4){
    print('true');
}else{
    print('false');
}

# 函数和闭包
def add(a,b){
    c = a+b;
    def tmp(){
        c+7;
    }
    tmp;
}
a = add(3,5);
print(a());


# 字典
attr = {
    'a': 1,
    56: 'hello'
};
print(attr['a']);
print(attr[56]);


# 类和对象
class A{
    v1 = 3 +5;
    def hello(self, name) {
        self.name = name;
        print('hello ', name);
    }
    add = add;
}

a = A();
print(A.add(2,6));
a.hello('world');

print(a.dict, A.dict);

# new 原生函数定义类,(相当于 python type 函数)
A = new('A', null, {'v1': 356});
print(A.v1);












