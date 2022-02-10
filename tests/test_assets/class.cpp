

static const char* MyClass::array2[] = {"Item1", "Item2"};

static const char* MyClass::array3[] = 
{
	"ItemNewline1",
	"ItemNewline2"
};

const size_t MyClass::Nested::m_gcAnswer  = 42;


int MyClass::GetParam() const 
{
	return m_var1;
}

/*virtual*/int MyClass::VirtualMethod()
{
}

/*virtual*/void MyClass::PureVirtualMethod() = 0
{
}

const size_t MyClass::Nested::m_gcAnswer  = 42;




/**
 * Example multiline documentation.
 */
void Example::DoNothing()
{
}

