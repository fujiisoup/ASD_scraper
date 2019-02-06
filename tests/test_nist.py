import numpy as np
import os
import pytest
import xarray as xr
from .. import nist


def test_lines():
    url = nist.get_line_url('Fe', 3)
    data = nist.get_lines('Fe', 3)
    # try export to netcdf
    filename = '_tmp'
    data.to_netcdf(filename)
    os.remove(filename)


@pytest.mark.parametrize(('element', 'nele'), [
    ['Li', 1], ['Li', 3], ['H', 1], ['N', 2], ['Ne', 3], ['Ne', 7], ['Mg', 9],
    ['Cl', 16]
    # ['F', 1] : not found
    ])
def test_fuse(element, nele):
    print(nist.get_line_url(element, nele))
    levels = nist.get_levels(element, nele)
    lines = nist.get_lines(element, nele)
    data = nist.fuse(levels, lines)
    assert data['S'].dtype == np.float
    assert (~data['Aki'].isnull()).sum() > 0
    assert (~data['fik'].isnull()).sum() > 0
    assert (~data['S'].isnull()).sum() > 0
    # try export to netcdf
    filename = '_tmp'
    data.to_netcdf(filename)
    os.remove(filename)


@pytest.mark.parametrize(('element', 'nele'), [
    ['F', 1], ['Mg', 1], ['Cr', 22]
    ])
def test_lines_notfound(element, nele):
    with pytest.raises(nist.DataNotFoundError):
        print(nist.get_line_url(element, nele))
        levels = nist.get_levels(element, nele)
        lines = nist.get_lines(element, nele)
        data = nist.fuse(levels, lines)


def test_levels():
    data = nist.get_levels('Fe', 3)
    assert np.allclose(data[0], 0.0)
    assert data[1]['Level(eV)_digits'] == 4
    assert data['Term'][0] == '2S'
    assert data['J'][0] == 1
    assert np.allclose(data[1], 48.5997)
    assert data['Term'][1] == '2P'
    assert data['parity'][1] == 'odd'
    assert data['J'][2] == 3
    assert np.allclose(data[-1], 7881.9)
    assert data['Term'][-1] == '2S'
    assert data['J'][-1] == 1

    assert 'Uncertainty(eV)' in data.coords
    assert 'Uncertainty (eV)' not in data.coords
    assert 'Reference' in data.coords

    assert data['Reference'][4] == 'L7185'
    assert data['Reference'][-1] == 'L7185'
    assert len(np.unique(data['Reference'])) == 1
    # try export to netcdf
    filename = '_tmp'
    data.to_netcdf(filename)
    os.remove(filename)


@pytest.mark.parametrize(('element', 'nele'), [
    ['Be', 3], ['F', 1], ['Mg', 8], ['As', 1],
    ['Na', 2]
    # ['N', 2], nitrogen has a duplicate entry for 1s 6d.
    ])
def test_levels2(element, nele):
    print(nist.get_level_url(element, nele))
    data = nist.get_levels(element, nele)
    assert data['Uncertainty(eV)'].dtype == float

    # not all revel is not uncertain
    assert not (data['Term_uncertain']).all()
    assert not (data['Configuration_uncertain']).all()
    # remove not-identified J
    da = data.isel(ilev=data['J'] > -1)
    # remove not identified configuration and term
    da = da.isel(ilev=~da['Configuration_uncertain'])
    da = da.isel(ilev=~da['Term_uncertain'])
    da = da.set_index(ilev=['Configuration', 'Term', 'J'])
    values, counts = np.unique(da['ilev'].values, return_counts=True)
    print(da)
    print(values[counts > 1])
    assert (counts == 1).all()


def test_levels_x():
    element = 'Ne'
    nele = 4
    print(nist.get_level_url(element, nele))
    data = nist.get_levels(element, nele)
    assert data.isnull().sum() == 0


def test_duplicate_J():
    data = nist.get_levels('Na', 2)
    assert len(data.isel(ilev=(data['Configuration'] == "1s.4f") *
                              (data['Term'] == "3F") *
                              (data['J'] == 4))) > 0
    assert len(data.isel(ilev=(data['Configuration'] == "1s.4f") *
                              (data['Term'] == "3F") *
                              (data['J'] == 6))) > 0
    assert len(data.isel(ilev=(data['Configuration'] == "1s.4f") *
                              (data['Term'] == "3F") *
                              (data['J'] == 8))) > 0


def test_is_theoretical():
    data = nist.get_levels('As', 1)
    assert data.isel(ilev=1)['Level(eV)_is_theoretical']
