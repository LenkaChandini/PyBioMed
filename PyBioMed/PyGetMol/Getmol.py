# -*- coding: utf-8 -*-
#  Copyright (c) 2016-2017, Zhijiang Yao, Jie Dong and Dongsheng Cao
#  All rights reserved.
#  This file is part of the PyBioMed.
#  The contents are covered by the terms of the BSD license
#  which is included in the file license.txt, found at the root
#  of the PyBioMed source tree.
"""
This module is to get different formats of molecules from file and web. If you

have any question please contact me via email.

Authors: Zhijiang Yao and Dongsheng Cao.

Date: 2016.06.04

Email: gadsby@163.com
"""

try:
    # Python 3
    from urllib.request import urlopen, Request
except ImportError:
    # Python 2
    from urllib2 import urlopen, Request
# Core Library modules
import os
import re
import string
import pybel

# Third party modules
from rdkit import Chem

Version = 1.0


def ReadMolFromSDF(filename=""):
    """
    Read a set of molecules by SDF file format.

    Note: the output of this function is a set of molecular objects.

    You need to use for statement to call each object.

    Usage:

        res=ReadMolFromSDF(filename)

        Input: filename is a file name with path.

        Output: res is a set of molecular object.

    """
    molset = Chem.SDMolSupplier(filename)
    return molset


def ReadMolFromMOL(filename=""):
    """
    Read a  molecule by mol file format.

    Usage:

        res=ReadMolFromMOL(filename)

        Input: filename is a file name with path.

        Output: res is a  molecular object.

    """
    mol = Chem.MolFromMolFile(filename)
    return mol


def ReadMolFromSmile(smi=""):
    """
    #################################################################
    Read a molecule by SMILES string.

    Usage:

        res=ReadMolFromSmile(smi)

        Input: smi is a SMILES string.

        Output: res is a molecule object.
    #################################################################
    """
    mol = Chem.MolFromSmiles(smi.strip())

    return mol


def ReadMolFromInchi(inchi=""):
    """
    #################################################################
    Read a molecule by Inchi string.

    Usage:

        res=ReadMolFromInchi(inchi)

        Input: inchi is a InChi string.

        Output: res is a molecule object.
    #################################################################
    """
    from openbabel import pybel

    temp = pybel.readstring("inchi", inchi)
    smi = temp.write("smi")
    mol = Chem.MolFromSmiles(smi.strip())

    return mol


def ReadMolFromMol(filename=""):
    """
    #################################################################
    Read a molecule with mol file format.

    Usage:

        res=ReadMolFromMol(filename)

        Input: filename is a file name.

        Output: res is a molecule object.
    #################################################################
    """
    mol = Chem.MolFromMolFile(filename)
    return mol


#############################################################################

def GetMolFromCAS(casid=""):
    """
    Download molecules from http://www.chemnet.com/cas/ using CAS ID (casid).
    Requires OpenBabel's pybel module.
    """
    casid = casid.strip()
    
    # Download page from chemnet
    link = f"http://www.chemnet.com/cas/supplier.cgi?terms={casid}&l=&exact=dict"
    localfile = urlopen(link)
    
    # Read and decode the content
    temp = [line.decode('utf-8') for line in localfile.readlines()]
    
    # Close the connection
    localfile.close()
    
    # Search for the InChI string in the page content
    res = None
    for i in temp:
        if "InChI=" in i:  # Check if the line contains "InChI="
            k = i.split('<td align="left">')
            kk = k[1].split("</td>\r\n")
            if kk[0].startswith("InChI"):
                res = kk[0].strip()
                break
    
    # Error handling if no InChI is found
    if res is None:
        raise ValueError(f"InChI string not found for CAS ID {casid}.")
    
    # Convert the InChI string to a molecule using pybel
    #mol = pybel.readstring("inchi", res)
    mol = pybel.Molecule(res)  # Use the Molecule constructor directly
    
    # Convert the molecule to SMILES format
    smile = mol.write("smi").strip()
    
    return smile


def GetMolFromEBI():
    """
    """
    pass


def GetMolFromNCBI(cid=""):
    """
    Downloading the molecules from http://pubchem.ncbi.nlm.nih.gov/ by cid (cid).
    """
    cid = cid.strip()
    localfile = urlopen(
        "http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid="
        + cid
        + "&disopt=SaveSDF"
    )
    temp = localfile.readlines()
    f = file("temp.sdf", "w")
    f.writelines(temp)
    f.close()
    localfile.close()
    m = Chem.MolFromMolFile("temp.sdf")
    os.remove("temp.sdf")
    temp = Chem.MolToSmiles(m, isomericSmiles=True)
    return temp


def GetMolFromDrugbank(dbid=""):
    """
    Downloading the molecules from http://www.drugbank.ca/ by dbid (dbid).
    """
    dbid = dbid.strip()
    link = "http://www.drugbank.ca/drugs/" + dbid + ".sdf"
    
    # Create a request with headers
    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    localfile = urlopen(req)
    lines = localfile.readlines()
    #print(lines)
    # Read and decode the contents of the file
    temp = [line.decode('utf-8') for line in lines]  # Decode each line
    #print(temp)
    with open("temp.sdf", "w") as f:
        f.write("".join(temp))  # Join the list into a single string and write it to the file
    
    # Close the files
    f.close()
    localfile.close()
    
    # Check if the file was written successfully
    if os.path.getsize("temp.sdf") == 0:
        raise ValueError("The downloaded SDF file is empty or corrupted.")
    
    # Load the molecule using RDKit
    m = Chem.MolFromMolFile("temp.sdf")
    
    #print(f"extracted data: {m}")
    
    # Check if the molecule was successfully loaded
    if m is None:
        raise ValueError("RDKit could not load the molecule from the SDF file.")
    
    # Convert the molecule to SMILES
    temp = Chem.MolToSmiles(m, isomericSmiles=True)
    
    # Remove the temporary SDF file
    os.remove("temp.sdf")
    
    return temp

def GetMolFromKegg(kid=""):
    """
    Downloading the molecules from http://www.genome.jp/ by kegg id (kid).
    """
    ID = str(kid)
    link = urlopen("http://www.genome.jp/dbget-bin/www_bget?-f+m+drug+" + ID)
    #temp = localfile.readlines()
    #f = open("temp.mol", "w")
    #f.writelines(temp)
    #f.close()
    #localfile.close()
    # Create a request with headers

    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    localfile = urlopen(req)
    lines = localfile.readlines()
    #print(lines)
    # Read and decode the contents of the file
    temp = [line.decode('utf-8') for line in lines]  # Decode each line
    #print(temp)
    with open("temp.sdf", "w") as f:
        f.write("".join(temp))  # Join the list into a single string and write it to the file
    
    # Close the files
    f.close()
    localfile.close()

    m = Chem.MolFromMolFile("temp.mol")
    os.remove("temp.mol")
    temp = Chem.MolToSmiles(m, isomericSmiles=True)
    return temp


#############################################################################

if __name__ == "__main__":
    print("-" * 10 + "START" + "-" * 10)
    print("Only PyBioMed is successfully installed the code below can be run！")
    from PyBioMed.PyGetMol.GetProtein import timelimited

    @timelimited(10)
    def run_GetMolFromCAS():
        temp = GetMolFromCAS(casid="50-12-4")
        print(temp)

    @timelimited(10)
    def run_GetMolFromNCBI():
        temp = GetMolFromNCBI(cid="2244")
        print(temp)

    @timelimited(10)
    def run_GetMolFromDrugbank():
        temp = GetMolFromDrugbank(dbid="DB00133")
        print(temp)

    @timelimited(10)
    def run_GetMolFromKegg():
        temp = GetMolFromKegg(kid="D02176")
        print(temp)

    run_GetMolFromCAS()
    print("-" * 25)
    run_GetMolFromNCBI()
    print("-" * 25)
    run_GetMolFromDrugbank()
    print("-" * 25)
    run_GetMolFromKegg()
    print("-" * 10 + "END" + "-" * 10)
