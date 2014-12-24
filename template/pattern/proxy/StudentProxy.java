@Proxy(
  type = Student,
  lazy = { profile },
  hide = { @Set(grade) }
)
class StudentProxy {
}
