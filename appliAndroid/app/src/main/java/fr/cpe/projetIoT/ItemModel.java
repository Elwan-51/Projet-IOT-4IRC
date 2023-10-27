package fr.cpe.projetIoT;

public class ItemModel {
    private String itemName;
    private int order;

    public ItemModel(String itemName) {
        this.itemName = itemName;
        // Initial order, peut être ajusté lors du réarrangement
        this.order = 0;
    }

    public String getItemName() {
        return itemName;
    }

    public int getOrder() {
        return order;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    @Override
    public String toString() {
        return "ItemModel{" +
                "itemName='" + itemName + '\'' +
                ", order=" + order +
                '}';
    }
}