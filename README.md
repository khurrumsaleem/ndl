<h1 align="center" style="font-family:simplifica">NDL</h1>


<h5 align="center">Nuclear Data Library processing tools.</h5>

<br>


NDL is a python package that can build NJOY (http://www.njoy21.io/) input with default settings and run NJOY in order to convert the nuclear data files from
[ENDF-6 format](https://www.oecd-nea.org/dbdata/data/manual-endf/endf102.pdf) into ACE files that can be employed in Serpent-2 (http://montecarlo.vtt.fi/) or MCNP (https://mcnp.lanl.gov/) codes.
The primary objective of the code is to process neutron and photo-atomic ENDF-6 files for Monte Carlo simulations.

 ***

## :wrench: Installation

To install NDL, run the following command:

```
git clone https://github.com/nicoloabrate/ndl.git
```
Then, add it to your python path or locally install it via pip
```
pip install path_to_ndl_parent_directoy/ndl/
```

To properly run NDL, you need [NJOY2016](https://github.com/njoy/NJOY2016) or [NJOY21](https://github.com/njoy/NJOY21) properly installed on your Linux machine.

<br>

## :notebook_with_decorative_cover: Documentation


<br>

## :telephone_receiver: Contacts

* [**Nicolo' Abrate**](http://www.nemo.polito.it/) - nicolo.abrate@polito.it

<br>

## :bookmark: Acknowledgments
The Serpent developers teams is thankfully aknowledged for having
shared the procedures used to prepare the energy deposition additional
data required in the ACE files.

<br>

## :clipboard: Reference

[NJOY2016](https://github.com/njoy/NJOY2016)
[Serpent 2 Monte Carlo code](http://montecarlo.vtt.fi/)
