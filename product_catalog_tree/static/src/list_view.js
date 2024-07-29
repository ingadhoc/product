/** @odoo-module **/

import { listView } from '@web/views/list/list_view';
import { registry } from "@web/core/registry";

import { ProductCatalogListController } from "./list_controller";

export const productCatalogListView = {
    ...listView,
    Controller: ProductCatalogListController,
};


registry.category("views").add("product_list_catalog", productCatalogListView);
