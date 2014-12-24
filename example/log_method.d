#!/usr/sbin/dtrace -s

/* https://blogs.oracle.com/damien/entry/dtrace_java_methods
 * http://www.exitcertified.com/newsletter/2007-march/resources/java_dtrace_program.pdf
 */

/*
 * args[0]: The Java thread ID of the thread that is entering or leaving the method
 * args[1]: A pointer to mUTF-8 string data which contains the name of the class of the method
 * args[2]: The length of the class name (in bytes)
 * args[3]: A pointer to mUTF-8 string data which contains the name of the method
 * args[4]: The length of the method name (in bytes)
 * args[5]: A pointer to mUTF-8 string data which contains the signature of the method
 * args[6]: The length of the signature (in bytes)
 */

#pragma D option quiet
/*
#pragma D option flowindent
*/

dtrace:::BEGIN
{
  pkg = "patterns";
  Main = "patterns/Main";
  main = "main";
}

hotspot$target:::method-entry
{
  self->cls_name = copyinstr(arg1, arg2);
  self->mtd_name = copyinstr(arg3, arg4);
}

hotspot$target:::method-entry
/strstr(self->cls_name, Main) != NULL && main == self->mtd_name/
{
  self->interested = 1;
  self->indent = -2;
}

hotspot$target:::method-entry
/strstr(self->cls_name, pkg) != NULL && self->interested/
{
  self->indent += 2;
  printf("%*s> %s.%s\n", self->indent, "", self->cls_name, self->mtd_name);
}

hotspot$target:::method-return
{
  self->cls_name = copyinstr(arg1, arg2);
  self->mtd_name = copyinstr(arg3, arg4);
}

hotspot$target:::method-return
/strstr(self->cls_name, pkg) != NULL && self->interested/
{
  printf("%*s< %s.%s\n", self->indent, "", self->cls_name, self->mtd_name);
  self->indent -= 2;
}

hotspot$target:::method-return
/strstr(self->cls_name, Main) != NULL && main == self->mtd_name/
{
  self->interested = 0;
}

dtrace:::ERROR
{
}
