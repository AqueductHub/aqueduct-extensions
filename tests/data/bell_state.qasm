OPENQASM 2.0;
include "qelib1.inc";

qreg a[1];
qreg b[1];
creg bits[2];

h a[0];
cx a[0], b[0];
measure a[0] -> bits[0];
measure b[0] -> bits[1];
