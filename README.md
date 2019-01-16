# A script to scraping NIST Atomic Spectral Databse.

## Copy right
Please be careful about the copy right of the database.
I do not recommend to upload the data to anywhere public.

## Requirement
To run the script, [xarray](https://xarray.pydata.org) is necessary to be installed in your environment.

## Usage
To donwload the atomic levels, use `get_levels`
```python
data = nist.get_levels('Fe', 3)
```
The above downloads all the atomic levels of Li-like (with 3 electrons) iron and stores data into a `xarray.Dataset` object.

To download the atomic transitions, use `get_lines`
```python
data = nist.get_lines('Fe', 3)
```
The above downloads all the atomic transitions of Li-like (with 3 electrons) iron and stores data into a `xarray.Dataset` object.

See [this notebook](Download_data.ipynb) for an example usage.
