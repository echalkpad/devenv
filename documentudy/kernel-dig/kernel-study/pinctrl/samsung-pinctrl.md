

### initial state

samsung,pin-pud = 	<0> NP
			<1> PD
			<2> reserved
			<3> PU

samsung,pin-function = 	<0> Input
			<1> Output
			<2> ~ <0xE> reserved
			<0xF> NWEINT

samsung,pin-val = 	<0> Low
			<1> High

samsung,pin-drv = 	<0> 1x
			<1> 2x
			<2> 3x
			<3> 4x

### sleep state

samsung,pin-con-pdn = 	<0> OUT0 Low
			<1> OUT1 High
			<2> Input
			<3> Previous state

samsung,pin-pud-pdn = 	<0> NP
			<1> PD
			<2> reserved
			<3> PU


Setting PU/PD is means that GPIO is set by PU/PD inside of AP internally.
So, There is no needs to set PU/PD at the AP side if there is PU/PD resister in
the circuit diagram.
 
