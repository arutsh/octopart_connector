# Octopart Connector and Octopart Connector MRP

[![License: LGPL-3](https://img.shields.io/badge/licence-LGPL--3-blue.png)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![Octopart connector](https://img.shields.io/badge/github-Octopart%20Connector-brightgreen?logo=github)](https://github.com/arutsh/octopart_connector)


* This module links odoo's inventory product to several part numbers on [Octopart](https://octopart.com) .
* Checks stock availability for the linked parts
* Computes Min cost of the product based on the data retrieved from octopart
* Stores all historical prices on odoo for future reports
* Allows to create Group of Vendors (e.g. Manufacturer, Authorised distributor, etc...) and group vendors



Configuration
=============
To be able to use Octopart Connector app, you should get API token from Octopart. For more information please refer to Octopart . Octopart Connector Retrieves only specs available for Basic version.

Octopart Connector>configuration
> Octopart Client URL: https://octopart.com/api/v4/endpoint


User Access Level
=================

App has 2 access level
* internal user
> all odoo user can see octopart tab on the product template page and link part to octopart if they have right to create/update product
* Inventory administrator
> * Have access to App page Octopart Connector
> * Can configure the app
> * Create Vendor Groups
> * Set Confirmed Vendors
> * Link Vendor with existing Contact
> * Access List of Available component history



Known issues / Roadmap
======================

* 28-05-2022: The app does not link product variants to octopart
* 28-05-2022: Stock is checked only once per day. meaning if user click on check stock availability today, first time it will retrieve data but will not update any more during the day. This limitation is set to prevent too much requests to Octopart.

Bug Tracker
===========

Bugs are tracked on [GitHub Issues](https://github.com/arutsh/octopart_connector/issues)
In case of trouble, please check there if your issue has already been reported.
If you found one, please report  it by providing a detailed and leave feedback


Credits
=======

Authors
~~~~~~~

* Arutshyan - ToolKit
* n.arutshyan(at)gmail.com
