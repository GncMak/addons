===================
Portal Stock Quants
===================
Credits
=======

Usage
=====
* Open "Contact & Address" on Partner and check "Show Quantities on Portal"

    .. image:: /static/src/img/img1.png
        :width: 15px

* Inventory on General Settings set "Stock Quants Domain" and "Stock Move Domain"

    .. image:: /static/src/img/img2.png
        :width: 15px

**Stock Quants Domain**

    ``[('location_id.usage', '=', 'internal'), ('reserved_quantity', '=', 0), ('product_tmpl_id.product_type', 'in',  [1,5])]``

**Stock Move Domain**

    ``[('product_tmpl_id.product_type', 'in', [1,5]), ('partner_id', '=', False), ('state', '=', 'assigned'), ('picking_type_id.code', '=', 'incoming')]``

Authors
~~~~~~~

* Serkan Sivriburun

Contributors
~~~~~~~~~~~~

* Konien Yazılım ve Danışmanlık Dış Tic. Ltd. Şti. <info@konien.com> (https://www.konien.com)

Other credits
~~~~~~~~~~~~~

This module is maintained by:

* Konien Yazılım ve Danışmanlık Dış Tic. Ltd. Şti.

Maintainers
~~~~~~~~~~~

This module is maintained by the Konien Yazılım ve Danışmanlık Dış Tic. Ltd. Şti.
