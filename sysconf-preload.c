#include <unistd.h>

long __sysconf(int name);

long sysconf(int name) {
  switch (name) {
    case _SC_NPROCESSORS_ONLN:
    case _SC_NPROCESSORS_CONF:
      return 1;
  }
  return __sysconf(name);
}

