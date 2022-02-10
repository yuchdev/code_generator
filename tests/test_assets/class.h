class MyClass 
{
public:
	enum Items
	{
		wdOne = 0,
		wdTwo = 1,
		wdThree = 2,
		wdItemsCount
	};
	
	struct Nested 
	{
		
		static const size_t m_gcAnswer;
		
	};
	
	int GetParam() const ;
	
	virtual int VirtualMethod();
	
	virtual void PureVirtualMethod() = 0;
	
	
private:
	int m_var1;
	
	int* m_var2;
	
	static const char* array2[];
	
	static const char* array3[];
	
};
/// An example
/// class with
/// multiline documentation
class Example 
{
public:
	void DoNothing();
	
	
private:
	/// A number.
	int m_var1;
	
};
