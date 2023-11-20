package fr.cpe.projetIoT;

/**
 * Class used to define items for managing the order in which values appear on the screen
 */
public class ItemModel {
    private String itemName;
    private int order;

    /**
     * Constructor for the ItemModel class.
     * @param itemName String representing the name of the item.
     */
    public ItemModel(String itemName) {
        this.itemName = itemName;
        this.order = 0;
    }

    /**
     * Get the name of the item.
     * @return itemName String
     */
    public String getItemName() {
        return itemName;
    }

    /**
     * Get the order of the item
     * @return order
     */
    public int getOrder() {
        return order;
    }

    /**
     * Set the order of the item
     * @param order int representing the new order of the item
     */
    public void setOrder(int order) {
        this.order = order;
    }

    /**
     * To help with debugging
     * @return toString
     */
    @Override
    public String toString() {
        return "ItemModel{" +
                "itemName='" + itemName + '\'' +
                ", order=" + order +
                '}';
    }
}