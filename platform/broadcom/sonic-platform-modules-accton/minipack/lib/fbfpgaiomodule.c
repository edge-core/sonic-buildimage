# Copyright (c) 2019 Edgecore Networks Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED ON AN  *AS IS* BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
# LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
# FOR A PARTICULAR PURPOSE, MERCHANTABLITY OR NON-INFRINGEMENT.
#
# See the Apache Version 2.0 License for specific language governing
# permissions and limitations under the License.

#include <Python.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>

//#define IDEBUG(...) printf(__VA_ARGS__)
#define IDEBUG(...)

#define FPGA_RESOURCE_NODE "/sys/devices/pci0000:00/0000:00:03.0/0000:05:00.0/resource0"
#define FPGA_RESOURCE_LENGTH 0x80000


static int hw_handle = -1;
static void *io_base = NULL;

static PyObject *fbfpgaio_hw_init(PyObject *self)
{
  const char fpga_resource_node[] = FPGA_RESOURCE_NODE;

  /* Open hardware resource node */
  hw_handle = open(fpga_resource_node, O_RDWR|O_SYNC);
  if (hw_handle == -1) {
    IDEBUG("[ERROR] %s: open hw resource node\n", __func__);
    return Py_False;
  }
  
  IDEBUG("[PASS] %s: open hw resource node\n", __func__);

  /* Mapping hardware resource */
  io_base = mmap(NULL, FPGA_RESOURCE_LENGTH, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_NORESERVE, hw_handle, 0);
  if (io_base == MAP_FAILED) {
    IDEBUG("[ERROR] %s: mapping resource node\n", __func__);
    perror("map_failed"); 
    fprintf(stderr,"%d %s\\n",errno,strerror(errno));
    return Py_False;
  }
  
  IDEBUG("[PASS] %s: mapping resource node\n", __func__);

  return Py_True; 
}

static PyObject *fbfpgaio_hw_release(PyObject *self)
{
  int retval = 0;

  if ((io_base != NULL) && (io_base != MAP_FAILED)) {
    retval = munmap(io_base, FPGA_RESOURCE_LENGTH);
    if (retval == 0) {
      IDEBUG("[PASS] %s: Unmapping hardware resources\n", __func__);
      close(hw_handle);
      return Py_True;
    }
  }

  IDEBUG("[ERROR] %s: unmapping resource node\n", __func__);
  return Py_False; 
}

static PyObject *fbfpgaio_hw_io(PyObject *self, PyObject *args)
{
  void *offset = NULL;
  /* We are not able to diffrentiate the input data between an unsigned value or a
     'None' object. We assume that the input data (if any) will be an unsigned integer.
     The default value of 'data' is larger than the max. number of unsigned integer.
     This value signify that the caller of this function does not input a data argument. */
  unsigned long input_data = 0x1FFFFFFFF;

  if (!PyArg_ParseTuple(args, "I|k", &offset, &input_data)) {
    return NULL;
  }

  if (input_data == 0x1FFFFFFFF) {
    // Read operation
    IDEBUG("Read operation\n");
    unsigned int *address = (unsigned int *) ((unsigned long) io_base + (unsigned long) offset);
    return Py_BuildValue("k", *address);
  } else {
    // Write operation
    IDEBUG("Write operation\n");
    unsigned int *address = (unsigned int *) ((unsigned long) io_base + (unsigned long) offset);
    unsigned int data = (unsigned int) (input_data & 0xFFFFFFFF);
    *address = data;

    Py_INCREF(Py_None);
    return Py_None;
  }
}

static PyMethodDef FbfpgaMethods[] = {
  { "hw_init", (PyCFunction) fbfpgaio_hw_init, METH_NOARGS, "Initialize resources for accessing FPGA" },
  { "hw_release", (PyCFunction) fbfpgaio_hw_release, METH_NOARGS, "Release resources for accessing FPGA" },
  { "hw_io", fbfpgaio_hw_io, METH_VARARGS, "Access FPGA" },
  { NULL, NULL, 0, NULL },
};

PyMODINIT_FUNC
initfbfpgaio(void)
{
  char docstr[] = "\
1. hw_init():\n\
   return value: True/False\n\
2. hw_release():\n\
   return value: True/False\n\
3. hw_io(offset,[data])\n\
   return value:\n\
     In reading operation: data which is read from FPGA\n\
     In writing operation: None\n";

  (void) Py_InitModule3("fbfpgaio", FbfpgaMethods, docstr);
}
