package fr.cpe.projetIoT;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

/**
 * Adapter class for managing data binding to the RecyclerView in the ItemModel.
 */
public class ItemAdapter extends RecyclerView.Adapter<ItemAdapter.ViewHolder> {

    private List<ItemModel> items;

    /**
     * Constructor for the ItemAdapter class.
     * @param items List of ItemModel objects.
     */
    public ItemAdapter(List<ItemModel> items) {
        this.items = items;
    }

    /**
     * Called when RecyclerView needs a new ViewHolder of the given type to represent an item.
     * @param parent ViewGroup into which the new View will be added.
     * @param viewType The view type of the new View.
     * @return ViewHolder for the RecyclerView.
     */
    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_layout, parent, false);
        return new ViewHolder(view);
    }

    /**
     * Called by RecyclerView to display the data at the specified position.
     * @param holder ViewHolder for the item to be displayed.
     * @param position The position of the item within the adapter's data set.
     */
    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        ItemModel item = items.get(position);
        holder.itemNameTextView.setText(item.getItemName());
    }

    /**
     * Retrieves the number of items in the List
     * @return int size
     */
    @Override
    public int getItemCount() {
        return items.size();
    }

    /**
     * ViewHolder class representing the individual items in the RecyclerView.
     */
    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView itemNameTextView;

        /**
         * Constructor for the ViewHolder class.
         * @param itemView View representing an individual item in the RecyclerView.
         */
        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            itemNameTextView = itemView.findViewById(R.id.itemNameTextView);
        }
    }
}
