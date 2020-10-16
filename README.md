
# Welcome to Panorama CDK Python project!

This project is WIP.


This is a set of tools to create the infrastructure needed for Panorama to run.
For more information about Panorama, please visit [https://aulasneo.com/en/panorama-analytics](https://aulasneo.com/en/panorama-analytics)

---

## How to get data from Open edX

### Tracking logs

Run the following command from CLI or add to a cron job:
```shell script
/usr/local/bin/aws s3 sync /edx/var/log/tracking/ s3://aulasneo-edxdata/logs/$LMS_BASE
```

### MySQL tables

Needs to be improved:

```shell script
TABLES="auth_user\
 student_courseenrollment\
 auth_userprofile\
 student_courseaccessrole\
 course_overviews_courseoverview\
 courseware_studentmodule\
 grades_persistentcoursegrade\
 student_manualenrollmentaudit\
 student_courseenrollmentallowed\
 certificates_generatedcertificate"

for TABLE in ${TABLES}
do
    LMSDIR="${REPORTDIR}/${TABLE}/lms=${LMS}"

    mkdir -p ${LMSDIR}

    REPORTFILE=${TABLE}.csv
    mysql -u root -b edxapp -e "SELECT * FROM ${TABLE};" | ${SCRIPTDIR=}/tab2csv.py > "${LMSDIR}/${REPORTFILE}"

done

/usr/local/bin/aws s3 sync ${REPORTDIR} ${REPORTBUCKET}

```

To convert mysql output to csv tab2csv.py:

```python
#!/usr/bin/env python

import csv
import sys


tab_in = csv.reader(sys.stdin, dialect=csv.excel_tab)
comma_out = csv.writer(sys.stdout, delimiter=',', doublequote=False, escapechar='\\')

for row in tab_in:
    comma_out.writerow(row)

```

---

# Text bellow this line comes from the original CDK readme file

---

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
