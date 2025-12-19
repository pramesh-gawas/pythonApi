
import pytest

def test_equal_or_not_equal():
    assert 2 == 2
    assert 3 == 3
    
def test_is_instance():
    assert isinstance("hello", str)
    assert isinstance("123", str)
    
    
    
def boolean_function():
    validate =True
    assert validate is True
    assert ('hello' == 'world')is False
    
def test_type_checking():
    assert type(100) is int
    assert type(3) is not float
  
  
def test_greater_less():
    assert 10 > 5
    assert 2 < 8
    assert 7 >= 7
    assert 4 <= 6
    
def test_list_membership():
    fruits = ['apple', 'banana', 'cherry']
    assert 'banana' in fruits
    assert 'grape' not in fruits
    
    
class Student:
    def __init__(self,first_name:str,last_name:str,major:str,year:int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = year
       
       
@pytest.fixture
def default_student():
    return Student("John","Doe","Computer Science",2)
       
def test_person_intialization(default_student):
    assert default_student.first_name == "John",'first name should be John'
    assert default_student.last_name == "Doe",'last name should be Doe'
    assert default_student.major == "Computer Science",'major should be Computer Science'
    assert default_student.year == 2  