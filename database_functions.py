import sqlite3
import csv, json
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_zillow_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Zillow;")
    curs.execute("CREATE TABLE IF NOT EXISTS Zillow (State TEXT PRIMARY KEY, Median_Home_Value INT);")

    with open("zillow.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Zillow
            VALUES (?, ?)
        '''

        for row in csvreader:
            curs.execute(insert_str, (
                row[0], #State
                row[1], #Median Home Value
            ))

    conn.commit()

def create_z2_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Zillow_Complete;")

    create_str = '''
        CREATE TABLE IF NOT EXISTS Zillow_Complete (
            State TEXT PRIMARY KEY,
            m1_31_1996 INT, m2_29_1996 INT, m3_31_1996 INT, m4_30_1996 INT, m5_31_1996 INT, m6_30_1996 INT, m7_31_1996 INT, m8_31_1996 INT, m9_30_1996 INT, m10_31_1996 INT, m11_30_1996 INT, m12_31_1996 INT, m1_31_1997 INT, m2_28_1997 INT, m3_31_1997 INT, m4_30_1997 INT, m5_31_1997 INT, m6_30_1997 INT, m7_31_1997 INT, m8_31_1997 INT, m9_30_1997 INT, m10_31_1997 INT, m11_30_1997 INT, m12_31_1997 INT, m1_31_1998 INT, m2_28_1998 INT, m3_31_1998 INT, m4_30_1998 INT, m5_31_1998 INT, m6_30_1998 INT, m7_31_1998 INT, m8_31_1998 INT, m9_30_1998 INT, m10_31_1998 INT, m11_30_1998 INT, m12_31_1998 INT, m1_31_1999 INT, m2_28_1999 INT, m3_31_1999 INT, m4_30_1999 INT, m5_31_1999 INT, m6_30_1999 INT, m7_31_1999 INT, m8_31_1999 INT, m9_30_1999 INT, m10_31_1999 INT, m11_30_1999 INT, m12_31_1999 INT, m1_31_2000 INT, m2_29_2000 INT, m3_31_2000 INT, m4_30_2000 INT, m5_31_2000 INT, m6_30_2000 INT, m7_31_2000 INT, m8_31_2000 INT, m9_30_2000 INT, m10_31_2000 INT, m11_30_2000 INT, m12_31_2000 INT, m1_31_2001 INT, 
            m2_28_2001 INT, m3_31_2001 INT, m4_30_2001 INT, m5_31_2001 INT, m6_30_2001 INT, m7_31_2001 INT, m8_31_2001 INT, m9_30_2001 INT, m10_31_2001 INT, m11_30_2001 INT, m12_31_2001 INT, m1_31_2002 INT, m2_28_2002 INT, m3_31_2002 INT, m4_30_2002 INT, m5_31_2002 INT, m6_30_2002 INT, m7_31_2002 INT, m8_31_2002 INT, m9_30_2002 INT, m10_31_2002 INT, m11_30_2002 INT, m12_31_2002 INT, m1_31_2003 INT, m2_28_2003 INT, m3_31_2003 INT, m4_30_2003 INT, m5_31_2003 INT, m6_30_2003 INT, m7_31_2003 INT, m8_31_2003 INT, m9_30_2003 INT, m10_31_2003 INT, m11_30_2003 INT, m12_31_2003 INT, m1_31_2004 INT, m2_29_2004 INT, m3_31_2004 INT, m4_30_2004 INT, m5_31_2004 INT, m6_30_2004 INT, m7_31_2004 INT, m8_31_2004 INT, m9_30_2004 INT, m10_31_2004 INT, m11_30_2004 INT, m12_31_2004 INT, m1_31_2005 INT, m2_28_2005 INT, m3_31_2005 INT, m4_30_2005 INT, m5_31_2005 INT, m6_30_2005 INT, m7_31_2005 INT, m8_31_2005 INT, m9_30_2005 INT, m10_31_2005 INT, m11_30_2005 INT, m12_31_2005 INT, m1_31_2006 INT, m2_28_2006 INT, m3_31_2006 INT, m4_30_2006 INT, m5_31_2006 INT, m6_30_2006 INT, m7_31_2006 INT, m8_31_2006 INT, m9_30_2006 INT, m10_31_2006 INT, m11_30_2006 INT, m12_31_2006 INT, m1_31_2007 INT, m2_28_2007 INT, m3_31_2007 INT, m4_30_2007 INT, m5_31_2007 INT, m6_30_2007 INT, m7_31_2007 INT, m8_31_2007 INT, m9_30_2007 INT, m10_31_2007 INT, m11_30_2007 INT, m12_31_2007 INT, m1_31_2008 INT, m2_29_2008 INT, m3_31_2008 INT, m4_30_2008 INT, m5_31_2008 INT, m6_30_2008 INT, m7_31_2008 INT, m8_31_2008 INT, m9_30_2008 INT, m10_31_2008 INT, m11_30_2008 INT, m12_31_2008 INT, m1_31_2009 INT, m2_28_2009 INT, m3_31_2009 INT, m4_30_2009 INT, m5_31_2009 INT, m6_30_2009 INT, m7_31_2009 INT, m8_31_2009 INT, m9_30_2009 INT, m10_31_2009 INT, m11_30_2009 INT, m12_31_2009 INT, m1_31_2010 INT, m2_28_2010 INT, m3_31_2010 INT, m4_30_2010 INT, m5_31_2010 INT, m6_30_2010 INT, m7_31_2010 INT, m8_31_2010 INT, m9_30_2010 INT, m10_31_2010 INT, m11_30_2010 INT, m12_31_2010 INT, m1_31_2011 INT, m2_28_2011 INT, m3_31_2011 INT, m4_30_2011 INT, m5_31_2011 INT, m6_30_2011 INT, m7_31_2011 INT, m8_31_2011 INT, m9_30_2011 INT, m10_31_2011 INT, m11_30_2011 INT, m12_31_2011 INT, m1_31_2012 INT, 
            m2_29_2012 INT, m3_31_2012 INT, m4_30_2012 INT, m5_31_2012 INT, m6_30_2012 INT, m7_31_2012 INT, m8_31_2012 INT, m9_30_2012 INT, m10_31_2012 INT, m11_30_2012 INT, m12_31_2012 INT, m1_31_2013 INT, m2_28_2013 INT, m3_31_2013 INT, m4_30_2013 INT, m5_31_2013 INT, m6_30_2013 INT, m7_31_2013 INT, m8_31_2013 INT, m9_30_2013 INT, m10_31_2013 INT, m11_30_2013 INT, m12_31_2013 INT, m1_31_2014 INT, m2_28_2014 INT, m3_31_2014 INT, m4_30_2014 INT, m5_31_2014 INT, m6_30_2014 INT, m7_31_2014 INT, m8_31_2014 INT, m9_30_2014 INT, m10_31_2014 INT, m11_30_2014 INT, m12_31_2014 INT, m1_31_2015 INT, m2_28_2015 INT, m3_31_2015 INT, m4_30_2015 INT, m5_31_2015 INT, m6_30_2015 INT, m7_31_2015 INT, m8_31_2015 INT, m9_30_2015 INT, m10_31_2015 INT, m11_30_2015 INT, m12_31_2015 INT, m1_31_2016 INT, m2_29_2016 INT, m3_31_2016 INT, m4_30_2016 INT, m5_31_2016 INT, m6_30_2016 INT, m7_31_2016 INT, m8_31_2016 INT, m9_30_2016 INT, m10_31_2016 INT, m11_30_2016 INT, m12_31_2016 INT, m1_31_2017 INT, m2_28_2017 INT, m3_31_2017 INT, m4_30_2017 INT, m5_31_2017 INT, m6_30_2017 INT, m7_31_2017 INT, m8_31_2017 INT, m9_30_2017 INT, m10_31_2017 INT, m11_30_2017 INT, m12_31_2017 INT, m1_31_2018 INT, m2_28_2018 INT, m3_31_2018 INT, m4_30_2018 INT, m5_31_2018 INT, m6_30_2018 INT, m7_31_2018 INT, m8_31_2018 INT, m9_30_2018 INT, m10_31_2018 INT, m11_30_2018 INT, m12_31_2018 INT, m1_31_2019 INT, m2_28_2019 INT, m3_31_2019 INT, m4_30_2019 INT, m5_31_2019 INT, m6_30_2019 INT, m7_31_2019 INT, m8_31_2019 INT, m9_30_2019 INT, m10_31_2019 INT, m11_30_2019 INT, m12_31_2019 INT, m1_31_2020 INT, m2_29_2020 INT, m3_31_2020 INT, m4_30_2020 INT, m5_31_2020 INT, m6_30_2020 INT, m7_31_2020 INT, m8_31_2020 INT, m9_30_2020 INT, m10_31_2020 INT, m11_30_2020 INT, m12_31_2020 INT, m1_31_2021 INT, m2_28_2021 INT
        )
    '''

    curs.execute(create_str)

    with open("zillow_by_state.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Zillow_Complete
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

        for row in csvreader:
            print(len(row))
            curs.execute(insert_str, (
                # row[0], #State
                # row[1], #Median Home Value
                row[5:]
            ))

    conn.commit()

def create_census_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Census;")
    curs.execute("CREATE TABLE IF NOT EXISTS Census (State TEXT PRIMARY KEY, Bachelor_Degrees INT);")

    with open("census.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Census
            VALUES (?, ?)
        '''
        for row in csvreader:
            curs.execute(insert_str, (
                row[0], #State
                row[1], #Bachelor Degrees
            ))

    conn.commit()

def create_wikipedia_table():
    conn = sqlite3.connect("project.db")
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS Wikipedia;")

    create_str = '''
        CREATE TABLE IF NOT EXISTS Wikipedia (
            State TEXT PRIMARY KEY,
            Per_Capita_Income INT,
            Median_Household_Income INT,
            Median_Family_Income INT,
            Population INT,
            Number_of_Households INT,
            Number_of_Families INT
            )
    '''
    curs.execute(create_str)
    with open("wikipedia.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        insert_str = '''
            INSERT INTO Wikipedia
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''

        for row in csvreader:
            curs.execute(insert_str, (
                row[0], #State
                row[1], #Per_Capita_Income
                row[2], #Median_Household_Income
                row[3], #Median_Family_Income
                row[4], #Population
                row[5], #Number_of_Households
                row[6], #Number_of_Families
            ))

    conn.commit()